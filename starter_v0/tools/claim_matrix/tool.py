from __future__ import annotations

from typing import Any

from tools._shared import terms


def build_claim_matrix(
    claims: list[str] | None = None,
    sources: list[dict[str, Any]] | None = None,
    min_overlap: int = 2,
    max_sources_per_claim: int = 3,
) -> dict[str, Any]:
    """Map claims to lexical support candidates without asserting truth."""
    claims = [str(claim).strip() for claim in (claims or []) if str(claim).strip()]
    sources = sources or []
    min_overlap = max(1, int(min_overlap or 2))
    max_sources_per_claim = max(1, min(int(max_sources_per_claim or 3), 10))

    source_terms = [
        terms(" ".join(str(source.get(field) or "") for field in ("title", "summary", "source")))
        for source in sources
    ]
    rows: list[dict[str, Any]] = []
    supported_count = 0

    for claim_index, claim in enumerate(claims):
        claim_terms = terms(claim)
        candidates: list[dict[str, Any]] = []
        for source_index, source in enumerate(sources):
            matched = sorted(claim_terms & source_terms[source_index])
            if len(matched) < min_overlap:
                continue
            denominator = max(1, len(claim_terms))
            candidates.append({
                "source_index": source_index,
                "title": source.get("title"),
                "url": source.get("url"),
                "source": source.get("source"),
                "matched_terms": matched,
                "overlap_count": len(matched),
                "coverage": round(len(matched) / denominator, 4),
            })
        candidates.sort(key=lambda item: (item["overlap_count"], item["coverage"]), reverse=True)
        candidates = candidates[:max_sources_per_claim]
        status = "candidate_found" if candidates else "no_candidate"
        if candidates:
            supported_count += 1
        rows.append({
            "claim_index": claim_index,
            "claim": claim,
            "status": status,
            "candidates": candidates,
        })

    return {
        "tool": "build_claim_matrix",
        "claim_count": len(claims),
        "source_count": len(sources),
        "claims_with_candidates": supported_count,
        "coverage_rate": round(supported_count / len(claims), 4) if claims else 0.0,
        "min_overlap": min_overlap,
        "rows": rows,
        "caveat": (
            "Lexical overlap identifies candidate evidence only. "
            "It does not verify that a claim is true or that a source entails it."
        ),
    }
