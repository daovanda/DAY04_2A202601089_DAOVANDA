from __future__ import annotations

import unittest

from tools.evidence_audit.tool import audit_evidence


class EvidenceAuditTests(unittest.TestCase):
    def test_passes_with_two_distinct_cited_sources(self) -> None:
        result = audit_evidence([
            {
                "title": "Primary release",
                "url": "https://example.com/release",
                "source": "example.com",
            },
            {
                "summary": "Independent analysis",
                "url": "https://analysis.example.org/report",
                "source": "analysis.example.org",
            },
        ])
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["unique_source_count"], 2)

    def test_reports_duplicates_missing_urls_and_low_diversity(self) -> None:
        result = audit_evidence([
            {"title": "A", "url": "https://example.com/a"},
            {"title": "A copy", "url": "https://example.com/a/"},
            {"title": "No citation"},
        ], min_sources=2)
        self.assertFalse(result["passed"])
        self.assertIn("https://example.com/a", result["issues"]["duplicate_urls"])
        self.assertEqual(result["issues"]["missing_url_indexes"], [2])
        self.assertFalse(result["checks"]["source_diversity"])


if __name__ == "__main__":
    unittest.main()
