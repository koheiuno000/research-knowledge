"""Parse optional expandable sections from paper summary Markdown (read-only)."""

from __future__ import annotations

import re


def extract_section(text: str, heading_pattern: str) -> str:
    m = re.search(
        rf"^##\s+{heading_pattern}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else ""


def markdown_to_plain_block(body: str, max_chars: int = 8000) -> str:
    """Light cleanup for HTML display; preserves structure as pre-wrap text."""
    if not body:
        return ""
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and "---" in stripped:
            continue
        lines.append(line)
    out = "\n".join(lines).strip()
    if len(out) > max_chars:
        out = out[: max_chars - 1] + "…"
    return out


def parse_researcher_takeaway_fields(text: str) -> dict[str, str]:
    section = extract_section(text, r"Researcher Takeaway")
    if not section:
        return {}
    fields: dict[str, str] = {}
    patterns = [
        ("establishes", r"\*\*Best use in my literature review:\*\*\s*([\s\S]*?)(?=\n\*\*|\Z)"),
        ("does_not_establish", r"\*\*Do not use this paper to claim:\*\*\s*([\s\S]*?)(?=\n\*\*|\Z)"),
        ("core_contribution_takeaway", r"\*\*Core contribution:\*\*\s*([\s\S]*?)(?=\n\*\*|\Z)"),
    ]
    for key, pat in patterns:
        m = re.search(pat, section, re.IGNORECASE)
        if m:
            fields[key] = re.sub(r"\s+", " ", m.group(1)).strip()
    return fields


def parse_secondary_relevance(text: str) -> str:
    section = extract_section(text, r"(?:12|10|9)\.\s+Relevance to My Study")
    if not section:
        return ""
    m = re.search(
        r"###\s+Useful(?:\s+[Cc]ontext|\s+counterpart)?[^\n]*\n([\s\S]*?)(?=###|\Z)",
        section,
    )
    if not m:
        m = re.search(
            r"###\s+Useful context[^\n]*\n([\s\S]*?)(?=###|\Z)",
            section,
            re.IGNORECASE,
        )
    if not m:
        return ""
    return markdown_to_plain_block(m.group(1).strip(), max_chars=4000)


def parse_doi_url(text: str) -> str | None:
    from .engine import extract_bold_field

    raw = extract_bold_field(text, "DOI / URL")
    if not raw:
        return None
    raw = raw.strip()
    if raw.lower().startswith("not reported"):
        return None
    if "doi.org" in raw.lower() or raw.lower().startswith("http"):
        return raw.split()[0] if raw.split()[0].startswith("http") else raw
    return None


def build_expandable_sections(text: str) -> dict[str, str]:
    """Return only sections that exist in the source summary."""
    sections: dict[str, str] = {}

    rq = extract_section(text, r"2\.\s+Research Question")
    if rq:
        sections["Research Question"] = markdown_to_plain_block(rq, 2000)

    for label, pat in (
        ("Sample / Evidence Base", r"(?:6|7|5)\.\s+Data and [Ss]ample"),
        ("Teacher Knowledge Measure", r"(?:4|5)\.\s+Teacher Knowledge"),
        ("Teaching Practice Measure", r"(?:5|6)\.\s+Teaching Practice"),
        ("Student Achievement Measure", r"(?:6|7)\.\s+Student Outcomes"),
        ("Identification Strategy", r"(?:8|7|6)\.\s+Methods and Identification"),
    ):
        body = extract_section(text, pat)
        if not body:
            if label == "Identification Strategy":
                body = extract_section(text, r"(?:7|6)\.\s+Methods(?:\s|\(|$)")
        if body:
            sections[label] = markdown_to_plain_block(body)

    for pat in (
        r"9\.\s+Main Findings(?:\s+\([^)]+\))?",
        r"8\.\s+Main [Ff]indings",
        r"9\.\s+Main [Ff]indings",
    ):
        body = extract_section(text, pat)
        if body:
            sections["Main Findings"] = markdown_to_plain_block(body)
            break

    takeaway = parse_researcher_takeaway_fields(text)
    if takeaway.get("establishes"):
        sections["What the Paper Establishes"] = takeaway["establishes"]
    if takeaway.get("does_not_establish"):
        sections["What the Paper Does Not Establish"] = takeaway["does_not_establish"]

    secondary = parse_secondary_relevance(text)
    if secondary:
        sections["Secondary Relevance"] = secondary

    return sections
