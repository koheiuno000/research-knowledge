"""Research-area paths for literature-review generation (extensible to multiple domains)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResearchAreaConfig:
    """Paths and display labels for one research area's evidence base."""

    slug: str
    title: str
    repo_root: Path

    @property
    def area_root(self) -> Path:
        return self.repo_root / self.slug

    @property
    def academic_papers(self) -> Path:
        return self.area_root / "academic-papers"

    @property
    def literature_review_dir(self) -> Path:
        return self.area_root / "literature-review"

    @property
    def references_bib(self) -> Path:
        return self.literature_review_dir / "references.bib"

    @property
    def output_markdown(self) -> Path:
        return self.literature_review_dir / "literature_review.md"

    @property
    def output_html(self) -> Path:
        return self.literature_review_dir / "literature_review.html"

    @property
    def summaries_path_display(self) -> str:
        return f"{self.slug}/academic-papers/"

    @property
    def references_bib_display(self) -> str:
        return f"{self.slug}/literature-review/references.bib"

    @property
    def relationship_taxonomy_json(self) -> Path:
        """Optional approved Effect Summary relationship labels for this area."""
        return self.literature_review_dir / "relationship_taxonomy.json"


def sb_cpd_config(repo_root: Path | None = None) -> ResearchAreaConfig:
    root = repo_root or Path(__file__).resolve().parents[2]
    return ResearchAreaConfig(
        slug="sb-cpd",
        title="SB-CPD / Teacher Development",
        repo_root=root,
    )


DEFAULT_RESEARCH_AREA = "sb-cpd"
