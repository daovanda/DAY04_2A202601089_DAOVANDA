from __future__ import annotations

import unittest

from tools import select_relevant_tools


def declaration(name: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": "",
            "parameters": {"type": "object", "properties": {}},
        },
    }


class ToolSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tools = [
            declaration(name)
            for name in (
                "clarify", "lookup", "social_search", "papers", "evidence_audit",
                "source_deduplicate", "claim_matrix", "citation_export",
            )
        ]

    def selected_names(self, content: str) -> set[str]:
        selected = select_relevant_tools([{"role": "user", "content": content}], self.tools)
        return {item["function"]["name"] for item in selected}

    def test_web_news_excludes_social_and_optional_research_tools(self) -> None:
        names = self.selected_names("Tin AI hôm nay có gì?")
        self.assertIn("lookup", names)
        self.assertNotIn("social_search", names)
        self.assertNotIn("papers", names)
        self.assertNotIn("evidence_audit", names)

    def test_explicit_web_and_twitter_keeps_social(self) -> None:
        names = self.selected_names("Tìm trên web và Twitter tin AI hôm nay.")
        self.assertIn("social_search", names)

    def test_serialized_switch_to_web_drops_old_social_intent(self) -> None:
        content = (
            "Conversation context for a multi-turn eval.\n"
            "- Earlier user turn 1: Mọi người nói gì trên Twitter?\n"
            "- Earlier user turn 2: Bỏ Twitter, chuyển sang tìm trên web.\n"
            "Latest user turn to answer now: Giữ chủ đề OpenAI"
        )
        names = self.selected_names(content)
        self.assertNotIn("social_search", names)

    def test_paper_and_audit_tools_are_intent_scoped(self) -> None:
        self.assertIn("papers", self.selected_names("Tìm 3 paper arXiv về RAG."))
        self.assertIn(
            "evidence_audit",
            self.selected_names("Audit source diversity cho các nguồn này."),
        )

    def test_bonus_tools_are_independently_intent_scoped(self) -> None:
        self.assertIn(
            "source_deduplicate",
            self.selected_names("Loại trùng các nguồn này theo URL."),
        )
        self.assertIn(
            "claim_matrix",
            self.selected_names("Tạo claim matrix cho các claim và source này."),
        )
        self.assertIn(
            "citation_export",
            self.selected_names("Xuất các nguồn này thành BibTeX citation."),
        )

    def test_bonus_tools_are_hidden_from_unrelated_web_query(self) -> None:
        names = self.selected_names("Tin AI hôm nay có gì?")
        self.assertNotIn("source_deduplicate", names)
        self.assertNotIn("claim_matrix", names)
        self.assertNotIn("citation_export", names)


if __name__ == "__main__":
    unittest.main()
