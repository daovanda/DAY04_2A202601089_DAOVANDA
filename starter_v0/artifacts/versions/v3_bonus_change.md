# v3-bonus — three additional team tools

## Goal

Meet the lab bonus threshold of more than three team-authored tools while
adding a coherent, testable research post-processing workflow.

## New tools

1. `source_deduplicate`: canonical URL/title duplicate removal with auditable
   duplicate groups.
2. `claim_matrix`: lexical claim-to-source candidate mapping with an explicit
   non-verification caveat.
3. `citation_export`: Markdown, APA-like, and BibTeX export without invented
   metadata.

Together with `evidence_audit`, the final submission has four team-authored
tools. All four are deterministic, read-only, task-scoped, documented, and
unit-tested.

## Evidence

- `data/eval_bonus.json`: 6 cases (3 single-turn + 3 multi-turn).
- `tests/test_bonus_tools.py`: direct behavior tests.
- Base regression is rerun under the same `v3-bonus` artifact to prove the
  expanded catalog does not regress mandatory routing.
