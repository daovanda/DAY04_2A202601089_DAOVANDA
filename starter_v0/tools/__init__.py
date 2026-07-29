from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from tools._shared import fold_text

# Folder names are intentionally vague to match the tool names students see.
# The imported function names are the underlying implementations (unchanged).
from .clarify.tool import ask_user
from .papers.tool import arxiv_search
from .paper_text.tool import get_arxiv_paper_text
from .timeline.tool import get_user_tweets
from .fetch.tool import read_url
from .format.tool import render_digest
from .policy.tool import search_company_policy
from .social_search.tool import search_tweets
from .send.tool import send_telegram
from .lookup.tool import web_search
from .evidence_audit.tool import audit_evidence
from .source_deduplicate.tool import deduplicate_sources
from .claim_matrix.tool import build_claim_matrix
from .citation_export.tool import export_citations


# NOTE (starter_v0): tool names here are intentionally vague. These keys are the
# names the model sees AND the names data/eval_base.json + data/eval_research_extension.json
# match against. If a team renames a tool, it MUST stay in sync across ALL of:
#   artifacts/tools.yaml  ->  this dict  ->  data/eval_base.json + data/eval_research_extension.json
# Otherwise the eval raises "not declared in tools.yaml" or scores every call as a name mismatch.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "timeline": get_user_tweets,
    "social_search": search_tweets,
    "lookup": web_search,
    "fetch": read_url,
    "format": render_digest,
    "send": send_telegram,
    "policy": search_company_policy,
    "papers": arxiv_search,
    "paper_text": get_arxiv_paper_text,
    "evidence_audit": audit_evidence,
    "source_deduplicate": deduplicate_sources,
    "claim_matrix": build_claim_matrix,
    "citation_export": export_citations,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]


def select_relevant_tools(
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expose optional/competing tools only when the active request needs them."""
    latest_user = next(
        (str(message.get("content", "")) for message in reversed(messages) if message.get("role") == "user"),
        "",
    )
    marker = "Latest user turn to answer now:"
    active_text = latest_user.split(marker, 1)[1] if marker in latest_user else latest_user
    full_folded = fold_text(latest_user)
    active_folded = fold_text(active_text)

    social_terms = ("twitter", "tweet", "mang xa hoi", "social media", " x ")
    social_active = any(term in active_folded for term in social_terms)
    if marker not in latest_user:
        social_active = social_active or any(term in full_folded for term in social_terms)
    switched_to_web = (
        ("bo twitter" in full_folded or "drop twitter" in full_folded)
        and ("sang web" in full_folded or "to web" in full_folded)
    )
    if switched_to_web and not any(term in active_folded for term in social_terms):
        social_active = False

    paper_active = any(term in active_folded for term in (
        "paper", "arxiv", "scientific article", "bai bao khoa hoc",
    ))
    audit_active = any(term in active_folded for term in (
        "audit", "evidence audit", "kiem tra chat luong", "chat luong nguon",
        "source quality", "source diversity",
    ))
    deduplicate_active = any(term in active_folded for term in (
        "deduplicate", "dedupe", "de-duplicate", "loai trung", "khu trung",
        "nguon trung", "duplicate source",
    ))
    claim_matrix_active = any(term in active_folded for term in (
        "claim matrix", "ma tran claim", "claim-source", "claim source",
        "anh xa claim", "evidence coverage",
    ))
    citation_active = any(term in active_folded for term in (
        "citation", "trich dan", "bibliography", "bibtex", "tai lieu tham khao",
        "xuat apa", "apa references",
    ))

    selected: list[dict[str, Any]] = []
    for item in tools:
        function = item.get("function", item)
        name = function.get("name")
        if name == "social_search" and not social_active:
            continue
        if name == "papers" and not paper_active:
            continue
        if name == "evidence_audit" and not audit_active:
            continue
        if name == "source_deduplicate" and not deduplicate_active:
            continue
        if name == "claim_matrix" and not claim_matrix_active:
            continue
        if name == "citation_export" and not citation_active:
            continue
        selected.append(item)
    return selected

