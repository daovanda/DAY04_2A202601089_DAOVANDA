from __future__ import annotations

import unittest

from tools.citation_export.tool import export_citations
from tools.claim_matrix.tool import build_claim_matrix
from tools.source_deduplicate.tool import deduplicate_sources


class SourceDeduplicateTests(unittest.TestCase):
    def test_canonicalizes_tracking_urls_and_preserves_first_item(self) -> None:
        items = [
            {"title": "Original", "url": "https://www.example.com/report/?utm_source=x"},
            {"title": "Copy", "url": "https://example.com/report"},
            {"title": "Other", "url": "https://other.org/item"},
        ]
        result = deduplicate_sources(items)
        self.assertEqual(result["unique_count"], 2)
        self.assertEqual(result["removed_count"], 1)
        self.assertEqual(result["unique_items"][0]["title"], "Original")
        self.assertEqual(result["duplicate_groups"][0]["duplicate_indexes"], [1])

    def test_falls_back_to_folded_title_when_url_is_missing(self) -> None:
        result = deduplicate_sources([
            {"title": "Trí tuệ nhân tạo"},
            {"title": "TRI TUE NHAN TAO"},
        ])
        self.assertEqual(result["unique_count"], 1)


class ClaimMatrixTests(unittest.TestCase):
    def test_maps_claim_to_ranked_candidate(self) -> None:
        result = build_claim_matrix(
            ["AI automates logistics operations"],
            [
                {
                    "title": "AI logistics platform",
                    "summary": "The platform automates complex logistics operations.",
                    "url": "https://example.com/a",
                },
                {"title": "Climate policy", "summary": "Emissions report."},
            ],
            min_overlap=2,
        )
        self.assertEqual(result["claims_with_candidates"], 1)
        self.assertEqual(result["rows"][0]["candidates"][0]["source_index"], 0)
        self.assertIn("does not verify", result["caveat"])

    def test_marks_claim_without_candidate(self) -> None:
        result = build_claim_matrix(
            ["Quantum battery breakthrough"],
            [{"title": "Marine biology", "summary": "Coral reef study"}],
            min_overlap=2,
        )
        self.assertEqual(result["rows"][0]["status"], "no_candidate")


class CitationExportTests(unittest.TestCase):
    def test_exports_markdown_and_apa_like_references(self) -> None:
        item = {
            "title": "Research Update",
            "url": "https://example.com/update",
            "authors": ["A. Nguyen", "B. Tran"],
            "published": "2026-07-29",
            "source": "Example Lab",
        }
        markdown = export_citations([item], style="markdown")
        apa = export_citations([item], style="apa")
        self.assertIn("[Research Update](https://example.com/update)", markdown["text"])
        self.assertIn("(2026). Research Update.", apa["text"])

    def test_exports_valid_bibtex_shape_without_inventing_url(self) -> None:
        result = export_citations(
            [{"title": "Untethered Evidence", "authors": ["A. Nguyen"]}],
            style="bibtex",
        )
        self.assertTrue(result["text"].startswith("@misc{"))
        self.assertIn("year = {n.d.}", result["text"])
        self.assertNotIn("url =", result["text"])


if __name__ == "__main__":
    unittest.main()
