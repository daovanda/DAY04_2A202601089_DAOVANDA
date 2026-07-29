from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlparse

from tools._shared import domain


def _normalized_url(value: str) -> str:
    parsed = urlparse((value or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def audit_evidence(
    items: list[dict[str, Any]] | None = None,
    min_sources: int = 2,
    require_urls: bool = True,
) -> dict[str, Any]:
    """Audit collected research items before synthesis or publication."""
    items = items or []
    min_sources = max(1, int(min_sources or 2))
    normalized_urls = [_normalized_url(str(item.get("url") or "")) for item in items]
    sources = [
        str(item.get("source") or domain(str(item.get("url") or ""))).strip().lower()
        for item in items
    ]
    sources = [source for source in sources if source]

    duplicate_counts = Counter(url for url in normalized_urls if url)
    duplicate_urls = sorted(url for url, count in duplicate_counts.items() if count > 1)
    missing_url_indexes = [index for index, url in enumerate(normalized_urls) if not url]
    missing_summary_indexes = [
        index for index, item in enumerate(items)
        if not str(item.get("summary") or item.get("title") or "").strip()
    ]
    unique_sources = sorted(set(sources))

    checks = {
        "has_items": bool(items),
        "source_diversity": len(unique_sources) >= min_sources,
        "urls_present": not missing_url_indexes if require_urls else True,
        "no_duplicate_urls": not duplicate_urls,
        "content_present": not missing_summary_indexes,
    }
    passed_checks = sum(1 for passed in checks.values() if passed)
    score = round(100 * passed_checks / len(checks), 1)

    recommendations: list[str] = []
    if not items:
        recommendations.append("Collect source items before running an evidence audit.")
    if len(unique_sources) < min_sources:
        recommendations.append(f"Add sources from at least {min_sources} distinct domains/accounts.")
    if require_urls and missing_url_indexes:
        recommendations.append("Add a valid http(s) URL to every cited item.")
    if duplicate_urls:
        recommendations.append("Remove duplicate URLs before synthesis.")
    if missing_summary_indexes:
        recommendations.append("Add a title or summary for every item.")

    return {
        "tool": "audit_evidence",
        "item_count": len(items),
        "unique_source_count": len(unique_sources),
        "unique_sources": unique_sources,
        "score": score,
        "passed": all(checks.values()),
        "checks": checks,
        "issues": {
            "duplicate_urls": duplicate_urls,
            "missing_url_indexes": missing_url_indexes,
            "missing_summary_indexes": missing_summary_indexes,
        },
        "recommendations": recommendations,
    }
