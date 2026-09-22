#!/usr/bin/env python3
"""
Build literature-review/literature_review.md from individual paper summaries.

Substantive source of truth: academic-papers/**/*.md (paper summaries)
Bibliographic source of truth: literature-review/references.bib
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ACADEMIC_PAPERS = REPO_ROOT / "academic-papers"
OUTPUT_PATH = REPO_ROOT / "literature-review" / "literature_review.md"
REFERENCES_BIB = REPO_ROOT / "literature-review" / "references.bib"

EXCLUDE_FILES = {"README.md", "paper_summary_template.md"}
EXCLUDE_DIRS = {"pdf"}

MATRIX_RELATIONSHIPS = [
    "PD → Teacher Knowledge",
    "PD → Teaching Practice",
    "PD → Student Achievement",
    "Teacher Knowledge → Teaching Practice",
    "Teaching Practice → Student Achievement",
    "Teacher Knowledge → Student Achievement",
    "Knowledge → Practice → Achievement",
]

RELATIONSHIP_ALIASES = {
    "pd → teacher knowledge": "PD → Teacher Knowledge",
    "pd → teaching practice": "PD → Teaching Practice",
    "pd → student achievement": "PD → Student Achievement",
    "teacher knowledge → teaching practice": "Teacher Knowledge → Teaching Practice",
    "teaching practice → student achievement": "Teaching Practice → Student Achievement",
    "teacher knowledge → student achievement": "Teacher Knowledge → Student Achievement",
    "knowledge → practice → achievement pathway": "Knowledge → Practice → Achievement",
    "knowledge → practice → achievement": "Knowledge → Practice → Achievement",
    "teacher knowledge → teaching practice → student achievement": "Knowledge → Practice → Achievement",
}

EVIDENCE_BY_RELATIONSHIP_SECTIONS = [
    ("PD → Teacher Knowledge", "### PD → Teacher Knowledge"),
    ("PD → Teaching Practice", "### PD → Teaching Practice"),
    ("PD → Student Achievement", "### PD → Student Achievement"),
    ("Teacher Knowledge → Teaching Practice", "### Teacher Knowledge → Teaching Practice"),
    ("Teaching Practice → Student Achievement", "### Teaching Practice → Student Achievement"),
    ("Teacher Knowledge → Student Achievement", "### Teacher Knowledge → Student Achievement"),
    ("Knowledge → Practice → Achievement", "### Knowledge → Practice → Achievement"),
]

CATEGORY_TITLES = {
    "01_teacher-knowledge": "01 — Teacher Knowledge",
    "02_teaching-practice": "02 — Teaching Practice",
    "03_student-achievement": "03 — Student Achievement",
    "04_knowledge-to-practice": "04 — Knowledge to Practice",
    "05_practice-to-achievement": "05 — Practice to Achievement",
    "06_knowledge-to-achievement": "06 — Knowledge to Achievement",
    "07_teacher-pd-interventions": "07 — Teacher PD Interventions",
    "08_reviews-and-synthesis": "08 — Reviews and Synthesis",
}


@dataclass
class EvidenceRow:
    relationship: str
    examined: str
    evidence_type: str
    notes: str


@dataclass
class PaperSummary:
    path: Path
    rel_path: str
    title_line: str
    short_title: str
    author_label: str
    category_folder: str
    category_label: str
    citation_key: str = "Not recorded"
    full_citation: str = "Not recorded"
    country_context: str = "Not recorded"
    paper_type: str = "Not recorded"
    primary_category: str = "Not recorded"
    research_question: str = "Not recorded"
    evidence_sample: str = "Not recorded"
    core_contribution: str = "Not recorded"
    key_findings: list[str] = field(default_factory=list)
    evidence_rows: list[EvidenceRow] = field(default_factory=list)
    relevance_sb_cpd: list[str] = field(default_factory=list)
    primary_role: str = "Not recorded"
    warnings: list[str] = field(default_factory=list)


def discover_summaries() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(ACADEMIC_PAPERS.rglob("*.md")):
        if path.name in EXCLUDE_FILES:
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        rel = path.relative_to(ACADEMIC_PAPERS)
        if len(rel.parts) < 2:
            continue
        if not re.match(r"^\d{2}_", rel.parts[0]):
            continue
        paths.append(path)
    return paths


def extract_bold_field(text: str, label: str) -> str | None:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)"
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return None
    value = m.group(1).strip()
    value = re.sub(r"`([^`]+)`", r"\1", value)
    return value.strip()


def extract_section(text: str, heading_pattern: str) -> str:
    m = re.search(
        rf"^##\s+{heading_pattern}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else ""


def parse_h1(title_line: str) -> tuple[str, str]:
    m = re.match(r"^#\s+(.+?)\s+—\s+(.+)$", title_line.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    rest = title_line.lstrip("# ").strip()
    return rest, rest


def normalize_relationship(raw: str) -> str | None:
    key = raw.strip().lower()
    key = re.sub(r"\s+", " ", key)
    return RELATIONSHIP_ALIASES.get(key)


def abbrev_evidence_type(raw: str, examined: str) -> str:
    if examined.strip().lower() not in ("yes", "y"):
        return "—"
    if not raw or raw.strip() in ("—", "-", ""):
        return "—"
    s = raw.lower()
    if "cross-study" in s or ("synthesis" in s and "review" in s):
        return "Cross-study synthesis"
    if "cross-study synthesis" in s:
        return "Cross-study synthesis"
    if "review of causal" in s:
        return "Cross-study synthesis"
    if "rct" in s:
        return "RCT"
    if "quasi" in s:
        return "QE"
    if "conceptual" in s:
        return "Conceptual"
    if "association" in s or "associational" in s:
        return "Association"
    if "descriptive" in s:
        return "Descriptive"
    return raw.split(";")[0].strip()[:40]


def parse_evidence_mapping_table(text: str) -> list[EvidenceRow]:
    section = extract_section(text, r"(?:\d+\.\s+)?Evidence Mapping")
    if not section:
        return []
    rows: list[EvidenceRow] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        rel_raw = cells[0]
        if rel_raw.lower() in ("relationship", "mark"):
            continue
        rel = normalize_relationship(rel_raw)
        if not rel and "→" in rel_raw:
            rel = rel_raw.strip()
        examined = cells[1] if len(cells) > 1 else ""
        etype = cells[2] if len(cells) > 2 else ""
        notes = cells[3] if len(cells) > 3 else ""
        if rel:
            rows.append(EvidenceRow(rel, examined, etype, notes))
    return rows


def parse_paper_type(text: str) -> str | None:
    m = re.search(
        r"\|\s*\*\*What type of paper is this\?\*\*\s*\|\s*\*\*(.+?)\*\*",
        text,
        re.DOTALL,
    )
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    pub = extract_bold_field(text, "Publication type")
    if pub:
        return pub
    return None


def parse_research_question(text: str) -> str:
    for pat in (r"2\.\s+Research Question", r"2\. Research Question"):
        body = extract_section(text, pat)
        if body:
            return re.sub(r"\s+", " ", body.split("\n\n")[0]).strip()
    return ""


def parse_sample_block(text: str) -> str:
    for pat in (
        r"6\.\s+Data and [Ss]ample",
        r"7\.\s+Data and [Ss]ample",
        r"5\.\s+Data and [Ss]ample",
    ):
        body = extract_section(text, pat)
        if body:
            lines = [ln.strip() for ln in body.splitlines() if ln.strip()][:4]
            return " ".join(lines)[:500]
    return ""


def parse_core_contribution(text: str) -> str:
    m = re.search(r"\*\*Core contribution:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)", text, re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    kt = extract_section(text, r"12\.\s+Key Takeaway")
    if kt:
        return re.sub(r"\s+", " ", kt.split("\n\n")[0]).strip()
    return ""


def parse_key_findings(text: str, max_items: int = 5) -> list[str]:
    findings: list[str] = []
    for pat in (
        r"9\.\s+Main Findings",
        r"8\.\s+Main Findings",
        r"Main Findings",
    ):
        body = extract_section(text, pat)
        if not body:
            continue
        for para in re.split(r"\n\n+", body):
            para = para.strip()
            if para.startswith("###"):
                continue
            if para.startswith("- "):
                findings.append(re.sub(r"\s+", " ", para[2:]).strip())
            elif para.startswith("**") and len(para) < 400:
                findings.append(re.sub(r"\s+", " ", para).strip())
        if findings:
            break
    if len(findings) < 3:
        cc = parse_core_contribution(text)
        if cc:
            findings.insert(0, cc)
    return findings[:max_items]


def parse_relevance(text: str, max_items: int = 4) -> list[str]:
    section = extract_section(text, r"(?:12|10|9)\.\s+Relevance to My Study")
    if not section:
        return []
    bullets: list[str] = []
    in_direct = False
    for line in section.splitlines():
        if re.match(r"###\s+Directly", line, re.I):
            in_direct = True
            continue
        if line.startswith("### ") and in_direct:
            break
        if in_direct and line.strip().startswith("- "):
            bullets.append(re.sub(r"\s+", " ", line.strip()[2:]).strip())
    if not bullets:
        for line in section.splitlines():
            if line.strip().startswith("- "):
                bullets.append(re.sub(r"\s+", " ", line.strip()[2:]).strip())
    return bullets[:max_items]


def infer_primary_role(category_folder: str) -> str:
    if category_folder == "07_teacher-pd-interventions":
        return "Individual PD intervention study"
    if category_folder == "08_reviews-and-synthesis":
        return "Review / cross-study synthesis"
    if category_folder.startswith("04_") or category_folder.startswith("05_") or category_folder.startswith("06_"):
        return "Direct relationship evidence"
    return "Construct or descriptive evidence"


def parse_summary(path: Path) -> PaperSummary:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(REPO_ROOT)
    category_folder = path.relative_to(ACADEMIC_PAPERS).parts[0]
    category_label = CATEGORY_TITLES.get(
        category_folder,
        category_folder.replace("_", " ").title(),
    )
    first_line = text.split("\n", 1)[0] if text else ""
    author_label, short_title = parse_h1(first_line)

    paper = PaperSummary(
        path=path,
        rel_path=str(rel).replace("\\", "/"),
        title_line=first_line,
        short_title=short_title,
        author_label=author_label,
        category_folder=category_folder,
        category_label=category_label,
        primary_role=infer_primary_role(category_folder),
    )

    ck = extract_bold_field(text, "Citation key")
    if ck:
        paper.citation_key = ck
    else:
        paper.warnings.append("Citation key")

    fc = extract_bold_field(text, "Full citation")
    if fc:
        paper.full_citation = fc

    ctx = extract_bold_field(text, "Country / Context") or extract_bold_field(
        text, "Country / context"
    )
    if ctx:
        paper.country_context = ctx
    else:
        paper.warnings.append("Country / Context")

    pc = extract_bold_field(text, "Primary category")
    if pc:
        paper.primary_category = pc

    pt = parse_paper_type(text)
    if pt:
        paper.paper_type = pt
    elif category_folder == "07_teacher-pd-interventions":
        paper.paper_type = "PD intervention evaluation (see summary)"
        paper.warnings.append("Paper type (explicit field missing; folder-based label only)")
    elif category_folder == "08_reviews-and-synthesis":
        paper.paper_type = "Review / cross-study synthesis (see summary)"
    else:
        paper.warnings.append("Paper type")

    rq = parse_research_question(text)
    if rq:
        paper.research_question = rq
    else:
        paper.warnings.append("Research question")

    sample = parse_sample_block(text)
    if sample:
        paper.evidence_sample = sample
    else:
        paper.warnings.append("Data and sample")

    cc = parse_core_contribution(text)
    if cc:
        paper.core_contribution = cc
    else:
        paper.warnings.append("Core contribution")

    paper.key_findings = parse_key_findings(text)
    paper.evidence_rows = parse_evidence_mapping_table(text)
    if not paper.evidence_rows:
        paper.warnings.append("Evidence Mapping table")

    paper.relevance_sb_cpd = parse_relevance(text)

    return paper


def load_bib_keys() -> list[tuple[str, str]]:
    if not REFERENCES_BIB.exists():
        return []
    content = REFERENCES_BIB.read_text(encoding="utf-8")
    labels: list[tuple[str, str]] = []
    for block in re.split(r"\n(?=@)", content):
        block = block.strip()
        if not block.startswith("@"):
            continue
        m = re.match(r"@\w+\{([^,\s]+)", block)
        if not m:
            continue
        key = m.group(1)
        author_m = re.search(r"author\s*=\s*\{([^}]+)\}", block, re.IGNORECASE)
        year_m = re.search(r"year\s*=\s*\{(\d{4})\}", block, re.IGNORECASE)
        if author_m:
            first = author_m.group(1).split(" and ")[0].strip()
            author = first.split(",")[0].strip() if "," in first else first.split()[0]
        else:
            author = key
        year = year_m.group(1) if year_m else "?"
        labels.append((key, f"{author} ({year})"))
    return labels


def matrix_cell(paper: PaperSummary, relationship: str) -> str:
    for row in paper.evidence_rows:
        if row.relationship != relationship:
            continue
        return abbrev_evidence_type(row.evidence_type, row.examined)
    return "—"


def examined_yes(paper: PaperSummary, relationship: str) -> bool:
    for row in paper.evidence_rows:
        if row.relationship == relationship:
            return row.examined.strip().lower() in ("yes", "y")
    return False


def compact_evidence_mapping(paper: PaperSummary) -> list[str]:
    lines = []
    for row in paper.evidence_rows:
        ex = row.examined.strip().lower()
        if ex in ("yes", "y"):
            ab = abbrev_evidence_type(row.evidence_type, row.examined)
            lines.append(f"- **{row.relationship}:** {ab}")
        elif ex in ("no", "n"):
            lines.append(f"- **{row.relationship}:** Not examined")
    return lines


def truncate(s: str, n: int = 120) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def build_markdown(papers: list[PaperSummary]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    categories = sorted({p.category_folder for p in papers})
    paper_types = sorted({p.paper_type for p in papers if p.paper_type != "Not recorded"})

    lines: list[str] = []
    lines.append("# Literature Review Evidence Base")
    lines.append("")
    lines.append(
        "> This file is generated from the individual paper summaries under "
        "`academic-papers/`. Do not manually edit paper-level evidence here. "
        "Update the source summary and regenerate this file."
    )
    lines.append("")
    lines.append(
        "> **Sources of truth:** substantive content → paper summaries; "
        "bibliographic metadata → `literature-review/references.bib`."
    )
    lines.append("")
    lines.append(f"*Generated: {generated}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(f"- **Total reviewed papers:** {len(papers)}")
    lines.append(f"- **Primary categories represented:** {len(categories)}")
    lines.append(f"- **Paper types represented:** {len(paper_types)}")
    if paper_types:
        for pt in paper_types:
            lines.append(f"  - {pt}")
    lines.append("")
    lines.append("Conceptual architecture (not all papers estimate every arrow):")
    lines.append("")
    lines.append("```")
    lines.append("Teacher PD / CPD")
    lines.append("        ↓")
    lines.append("Teacher Professional Knowledge")
    lines.append("        ↓")
    lines.append("Teaching Practice")
    lines.append("        ↓")
    lines.append("Student Achievement")
    lines.append("```")
    lines.append("")
    lines.append(
        "Some papers evaluate a **specific PD intervention** (folder 07); others "
        "**review or synthesize** evidence across programs (folder 08); others may "
        "directly examine single arrows (folders 04–06)."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Evidence Base at a Glance")
    lines.append("")
    lines.append(
        "| Citation | Context | Paper Type | Primary Category | Main Contribution |"
    )
    lines.append("|----------|---------|------------|------------------|-------------------|")
    for p in sorted(papers, key=lambda x: (x.category_folder, x.citation_key)):
        cite = f"`{p.citation_key}`" if p.citation_key != "Not recorded" else p.author_label
        lines.append(
            f"| {cite} | {truncate(p.country_context, 80)} | {truncate(p.paper_type, 50)} "
            f"| `{p.category_folder}` | {truncate(p.core_contribution, 100)} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Evidence Map")
    lines.append("")
    header = "| Paper | " + " | ".join(MATRIX_RELATIONSHIPS) + " |"
    sep = "|-------|" + "|".join(["---"] * len(MATRIX_RELATIONSHIPS)) + "|"
    lines.append(header)
    lines.append(sep)
    for p in sorted(papers, key=lambda x: x.citation_key):
        label = p.citation_key if p.citation_key != "Not recorded" else p.author_label
        cells = [matrix_cell(p, rel) for rel in MATRIX_RELATIONSHIPS]
        lines.append("| " + label + " | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        "**Legend:** RCT = randomized trial (or ITT from RCT); QE = quasi-experimental; "
        "Association = associational/correlational; Cross-study synthesis = synthesis across "
        "multiple studies/programs (not a new single-program causal estimate); Conceptual = "
        "conceptual discussion only; — = not examined in that paper."
    )
    lines.append("")
    lines.append(
        "*A PD study with separate outcomes on knowledge and practice does **not** "
        "count as evidence on Teacher Knowledge → Teaching Practice unless that "
        "relationship is directly estimated. Cross-program associations are not causal "
        "estimates of PD features.*"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Papers by Primary Category")
    lines.append("")

    by_cat: dict[str, list[PaperSummary]] = {}
    for p in papers:
        by_cat.setdefault(p.category_folder, []).append(p)

    for cat in sorted(by_cat.keys()):
        lines.append(f"### {CATEGORY_TITLES.get(cat, cat)}")
        lines.append("")
        for p in sorted(by_cat[cat], key=lambda x: x.citation_key):
            lines.append(f"#### {p.author_label} — {p.short_title}")
            lines.append("")
            lines.append(f"**Citation key:** `{p.citation_key}`")
            lines.append("")
            lines.append(f"**Context:** {p.country_context}")
            lines.append("")
            lines.append(f"**Paper type:** {p.paper_type}")
            lines.append("")
            lines.append(f"**Primary role:** {p.primary_role}")
            lines.append("")
            lines.append("**Main contribution**")
            lines.append("")
            lines.append(p.core_contribution if p.core_contribution != "Not recorded" else "Not recorded")
            lines.append("")
            lines.append("**Key findings**")
            lines.append("")
            if p.key_findings:
                for bf in p.key_findings:
                    lines.append(f"- {bf}")
            else:
                lines.append("- Not recorded")
            lines.append("")
            lines.append("**Evidence Mapping**")
            lines.append("")
            em = compact_evidence_mapping(p)
            if em:
                lines.extend(em)
            else:
                lines.append("- Not recorded")
            lines.append("")
            lines.append("**Relevance to SB-CPD**")
            lines.append("")
            if p.relevance_sb_cpd:
                for r in p.relevance_sb_cpd:
                    lines.append(f"- {r}")
            else:
                lines.append("- Not recorded")
            lines.append("")
            lines.append(f"**Source summary:** `{p.rel_path}`")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 5. Evidence by Relationship")
    lines.append("")

    for rel, heading in EVIDENCE_BY_RELATIONSHIP_SECTIONS:
        lines.append(heading)
        lines.append("")
        contributors = [p for p in papers if examined_yes(p, rel)]
        if not contributors:
            lines.append("**No directly reviewed evidence yet.**")
            lines.append("")
            continue
        for p in contributors:
            row = next(r for r in p.evidence_rows if r.relationship == rel)
            ab = abbrev_evidence_type(row.evidence_type, row.examined)
            note = truncate(row.notes, 200) if row.notes else p.core_contribution
            if p.category_folder == "08_reviews-and-synthesis" and ab == "Cross-study synthesis":
                note = (
                    "Cross-program associations across evaluated PD studies; "
                    "not causal estimates of PD features. " + truncate(row.notes or "", 150)
                )
            lines.append(f"- **`{p.citation_key}`** ({ab}): {note}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 6. Reviews and Conceptual Foundations")
    lines.append("")
    review_papers = [p for p in papers if p.category_folder == "08_reviews-and-synthesis"]
    if not review_papers:
        lines.append("*No papers in category 08 yet.*")
    else:
        for p in review_papers:
            lines.append(
                f"- **`{p.citation_key}`** — {p.short_title}: "
                f"{truncate(p.core_contribution, 280)} "
                f"*(Role: {p.primary_role}; not an individual PD intervention RCT.)*"
            )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 7. References")
    lines.append("")
    lines.append(
        "Full verified bibliographic metadata is maintained in "
        "`literature-review/references.bib`."
    )
    lines.append("")
    for key, label in load_bib_keys():
        lines.append(f"- `{key}` — {label}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*End of generated literature review evidence base.*")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    paths = discover_summaries()
    if not paths:
        print("WARNING: No paper summaries found under academic-papers/", file=sys.stderr)
        return 1

    papers = [parse_summary(p) for p in paths]
    for p in papers:
        for w in p.warnings:
            print(f"WARNING [{p.path.name}]: missing or partial field — {w}", file=sys.stderr)

    md = build_markdown(papers)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} ({len(papers)} papers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
