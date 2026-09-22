"""
Research-area relationship taxonomies for Effect Summary validation.

The core Effect Summary parser is taxonomy-agnostic. Each research area may
provide literature-review/relationship_taxonomy.json listing approved Relationship
labels. Unknown labels are flagged for researcher review, not auto-approved.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import ResearchAreaConfig
from .effect_summary import EffectRow


@dataclass(frozen=True)
class RelationshipEntry:
    label: str
    kind: str = ""
    summary: str = ""


@dataclass(frozen=True)
class RelationshipTaxonomy:
    research_area: str
    relationships: tuple[RelationshipEntry, ...]
    relationship_aliases: dict[str, str] = field(default_factory=dict)

    @property
    def approved_labels(self) -> frozenset[str]:
        return frozenset(e.label for e in self.relationships)

    def normalize_label(self, raw: str) -> tuple[str, bool]:
        """
        Map raw Relationship text to an approved label if possible.

        Returns (label, is_unknown). is_unknown True means not in approved set
        after alias lookup — flag as Proposed new relationship for review.
        """
        cleaned = re.sub(r"\s+", " ", raw.strip())
        if cleaned in self.approved_labels:
            return cleaned, False
        key = cleaned.lower()
        if key in self.relationship_aliases:
            canonical = self.relationship_aliases[key]
            return canonical, canonical not in self.approved_labels
        for alias, canonical in self.relationship_aliases.items():
            if alias.lower() == key:
                return canonical, canonical not in self.approved_labels
        return cleaned, True


@dataclass
class TaxonomyValidationIssue:
    relationship: str
    message: str
    proposed_new: bool = True


def taxonomy_path_for_area(area: ResearchAreaConfig) -> Path:
    return area.literature_review_dir / "relationship_taxonomy.json"


def load_taxonomy(area: ResearchAreaConfig) -> RelationshipTaxonomy | None:
    path = taxonomy_path_for_area(area)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = tuple(
        RelationshipEntry(
            label=item["label"],
            kind=item.get("kind", ""),
            summary=item.get("summary", ""),
        )
        for item in data.get("relationships", [])
    )
    aliases = {k: v for k, v in (data.get("relationship_aliases") or {}).items()}
    return RelationshipTaxonomy(
        research_area=data.get("research_area", area.slug),
        relationships=entries,
        relationship_aliases=aliases,
    )


def validate_effect_relationships(
    rows: list[EffectRow],
    taxonomy: RelationshipTaxonomy | None,
) -> list[TaxonomyValidationIssue]:
    if taxonomy is None or not rows:
        return []
    issues: list[TaxonomyValidationIssue] = []
    seen: set[str] = set()
    for row in rows:
        if not row.relationship or row.relationship in seen:
            continue
        seen.add(row.relationship)
        _canonical, unknown = taxonomy.normalize_label(row.relationship)
        if unknown:
            issues.append(
                TaxonomyValidationIssue(
                    relationship=row.relationship,
                    message=(
                        "Effect Summary relationship not in approved taxonomy "
                        f"for {taxonomy.research_area} — Proposed new relationship; "
                        "researcher approval required before adding to "
                        "relationship_taxonomy.json"
                    ),
                    proposed_new=True,
                )
            )
    return issues


def get_taxonomy(area: ResearchAreaConfig) -> RelationshipTaxonomy | None:
    """Load taxonomy for a research area, or None if not defined yet."""
    return load_taxonomy(area)
