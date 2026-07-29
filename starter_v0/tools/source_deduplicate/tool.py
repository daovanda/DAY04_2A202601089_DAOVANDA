from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from tools._shared import fold_text


TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}


def _canonical_url(value: str) -> str:
    parsed = urlparse((value or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMS
    ]
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower().removeprefix("www."),
        path,
        "",
        urlencode(query),
        "",
    ))


def _title_key(value: str) -> str:
    return " ".join(fold_text(value or "").split())


def deduplicate_sources(
    items: list[dict[str, Any]] | None = None,
    strategy: str = "url_or_title",
    preserve_order: bool = True,
) -> dict[str, Any]:
    """Remove duplicate source items while retaining duplicate-group evidence."""
    items = items or []
    strategy = strategy if strategy in {"url", "title", "url_or_title"} else "url_or_title"
    keyed: dict[str, list[int]] = {}
    unkeyed_counter = 0

    for index, item in enumerate(items):
        url_key = _canonical_url(str(item.get("url") or ""))
        title_key = _title_key(str(item.get("title") or ""))
        if strategy == "url":
            raw_key = f"url:{url_key}" if url_key else ""
        elif strategy == "title":
            raw_key = f"title:{title_key}" if title_key else ""
        else:
            raw_key = f"url:{url_key}" if url_key else (f"title:{title_key}" if title_key else "")
        if not raw_key:
            raw_key = f"unkeyed:{unkeyed_counter}"
            unkeyed_counter += 1
        keyed.setdefault(raw_key, []).append(index)

    kept_indexes = [indexes[0] for indexes in keyed.values()]
    if preserve_order:
        kept_indexes.sort()
    unique_items = [items[index] for index in kept_indexes]
    duplicate_groups = [
        {
            "key": key,
            "kept_index": indexes[0],
            "duplicate_indexes": indexes[1:],
        }
        for key, indexes in keyed.items()
        if len(indexes) > 1
    ]

    return {
        "tool": "deduplicate_sources",
        "strategy": strategy,
        "preserve_order": bool(preserve_order),
        "input_count": len(items),
        "unique_count": len(unique_items),
        "removed_count": len(items) - len(unique_items),
        "unique_items": unique_items,
        "duplicate_groups": duplicate_groups,
    }
