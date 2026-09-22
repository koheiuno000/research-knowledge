"""Minimal safe Markdown → HTML for paper detail blocks (offline, no dependencies)."""

from __future__ import annotations

import html
import re


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def markdown_to_html(text: str) -> str:
    if not text.strip():
        return ""
    lines = text.splitlines()
    out: list[str] = []
    in_ul = False
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            joined = " ".join(para).strip()
            if joined:
                out.append(f"<p>{_inline(joined)}</p>")
            para = []

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            flush_para()
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline(stripped[2:].strip())}</li>")
            continue
        close_ul()
        if not stripped:
            flush_para()
            continue
        if stripped.startswith("###"):
            flush_para()
            out.append(f"<h5>{_inline(stripped.lstrip('#').strip())}</h5>")
            continue
        para.append(stripped)
    close_ul()
    flush_para()
    return "\n".join(out)
