"""Display metadata for research areas (no paper findings)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import ResearchAreaConfig, sb_cpd_config


@dataclass(frozen=True)
class HubDisplayConfig:
    """Configurable hub authorship / update line (single source for generated HTML)."""

    author: str = "Dr. Kohei Uno"
    updated_label: str = "September 22, 2026"


DEFAULT_HUB_DISPLAY = HubDisplayConfig()


@dataclass(frozen=True)
class ResearchAreaDisplay:
    slug: str
    name: str
    card_title: str
    topic_tags: tuple[str, ...]
    icon_id: str
    short_description: str
    config_factory: Callable[[Path], ResearchAreaConfig]
    html_relative_from_dashboard: str


def all_research_areas(repo_root: Path) -> list[ResearchAreaDisplay]:
    _ = repo_root
    return [
        ResearchAreaDisplay(
            slug="sb-cpd",
            name="Teacher Development / SB-CPD",
            card_title="Teacher Development / SB-CPD",
            topic_tags=("Teachers", "Classroom", "Learning"),
            icon_id="teachers",
            short_description="School-based CPD and teacher development evidence.",
            config_factory=lambda root: sb_cpd_config(root),
            html_relative_from_dashboard="../sb-cpd/literature-review/literature_review.html",
        ),
        ResearchAreaDisplay(
            slug="preschool-impact",
            name="Preschool / Early Childhood Education",
            card_title="Preschool / Early Childhood",
            topic_tags=("Early Learning", "Child Development"),
            icon_id="preschool",
            short_description="Preschool and early childhood impact evidence.",
            config_factory=lambda root: ResearchAreaConfig(
                slug="preschool-impact",
                title="Preschool / Early Childhood",
                repo_root=root,
            ),
            html_relative_from_dashboard="",
        ),
        ResearchAreaDisplay(
            slug="edtech-ai",
            name="EdTech / AI in Education",
            card_title="EdTech / AI",
            topic_tags=("Technology", "AI", "Innovation"),
            icon_id="edtech",
            short_description="Educational technology and AI in education.",
            config_factory=lambda root: ResearchAreaConfig(
                slug="edtech-ai",
                title="EdTech / AI",
                repo_root=root,
            ),
            html_relative_from_dashboard="",
        ),
        ResearchAreaDisplay(
            slug="skills-tvet",
            name="Skills Development / TVET",
            card_title="Skills / TVET",
            topic_tags=("Skills", "Employment", "Training"),
            icon_id="tvet",
            short_description="Skills development and TVET evidence.",
            config_factory=lambda root: ResearchAreaConfig(
                slug="skills-tvet",
                title="Skills / TVET",
                repo_root=root,
            ),
            html_relative_from_dashboard="",
        ),
        ResearchAreaDisplay(
            slug="climate-education",
            name="Climate Change and Education",
            card_title="Climate & Education",
            topic_tags=("Climate", "Resilience", "Sustainability"),
            icon_id="climate",
            short_description="Climate change and education evidence.",
            config_factory=lambda root: ResearchAreaConfig(
                slug="climate-education",
                title="Climate Education",
                repo_root=root,
            ),
            html_relative_from_dashboard="",
        ),
    ]
