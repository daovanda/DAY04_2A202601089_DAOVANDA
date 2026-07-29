from __future__ import annotations

import re
from typing import Any

from tools._shared import domain, fold_text


def _authors(item: dict[str, Any]) -> str:
    value = item.get("authors") or item.get("author") or item.get("source") or domain(str(item.get("url") or ""))
    if isinstance(value, list):
        return ", ".join(str(author).strip() for author in value if str(author).strip())
    return str(value or "Unknown author").strip()


def _year(item: dict[str, Any]) -> str:
    value = str(item.get("published") or item.get("date") or item.get("year") or "")
    match = re.search(r"\b(19|20)\d{2}\b", value)
    return match.group(0) if match else "n.d."


def _bib_key(item: dict[str, Any], index: int) -> str:
    author = _authors(item).split(",", 1)[0].split()[-1]
    title_terms = re.findall(r"[a-z0-9]+", fold_text(str(item.get("title") or "")))
    title_part = "".join(term.capitalize() for term in title_terms[:2]) or "Source"
    year = _year(item).replace(".", "")
    raw = re.sub(r"[^A-Za-z0-9]", "", f"{author}{year}{title_part}")
    return raw or f"Source{index + 1}"


def export_citations(
    items: list[dict[str, Any]] | None = None,
    style: str = "markdown",
    include_abstract: bool = False,
) -> dict[str, Any]:
    """Export source items as Markdown, APA-like, or BibTeX citations."""
    items = items or []
    style = style if style in {"markdown", "apa", "bibtex"} else "markdown"
    citations: list[str] = []

    for index, item in enumerate(items):
        title = str(item.get("title") or "Untitled source").strip()
        url = str(item.get("url") or "").strip()
        authors = _authors(item)
        year = _year(item)
        source = str(item.get("source") or domain(url) or "").strip()
        summary = " ".join(str(item.get("summary") or "").split())

        if style == "apa":
            citation = f"{authors}. ({year}). {title}."
            if source and source.lower() not in authors.lower():
                citation += f" {source}."
            if url:
                citation += f" {url}"
        elif style == "bibtex":
            key = _bib_key(item, index)
            fields = [
                f"  title = {{{title.replace('{', '').replace('}', '')}}}",
                f"  author = {{{authors.replace('{', '').replace('}', '')}}}",
                f"  year = {{{year}}}",
            ]
            if url:
                fields.append(f"  url = {{{url}}}")
            if include_abstract and summary:
                fields.append(f"  note = {{{summary.replace('{', '').replace('}', '')}}}")
            citation = f"@misc{{{key},\n" + ",\n".join(fields) + "\n}"
        else:
            label = f"[{title}]({url})" if url else title
            metadata = " · ".join(part for part in (authors, year, source) if part)
            citation = f"{index + 1}. {label}" + (f" — {metadata}" if metadata else "")
            if include_abstract and summary:
                citation += f"\n   {summary}"
        citations.append(citation)

    separator = "\n\n" if style == "bibtex" else "\n"
    return {
        "tool": "export_citations",
        "style": style,
        "citation_count": len(citations),
        "citations": citations,
        "text": separator.join(citations),
    }
