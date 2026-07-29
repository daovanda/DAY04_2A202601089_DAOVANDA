# claim_matrix

## Purpose

Build an auditable claim-to-source candidate matrix using lexical overlap. It
helps identify claims with no candidate evidence before a report is published.

This is a team-authored bonus tool. It is deterministic, read-only, and never
claims to verify truth or semantic entailment.

## Use when

- The user explicitly asks for a claim matrix, claim–source mapping, evidence
  coverage table, or claims lacking candidate citations.
- Claims and source items already exist in the conversation.

## Do not use when

- The user asks to retrieve sources first.
- The user asks for a definitive fact-check; lexical overlap alone is not
  truth verification.
- The user only needs duplicate removal or citation formatting.

## Arguments

- `claims` (required): list of claim strings.
- `sources` (required): items with title/summary and preferably URL/source.
- `min_overlap` (default `2`): minimum shared meaningful terms.
- `max_sources_per_claim` (default `3`, maximum `10`): candidate limit.

## Output

Returns one row per claim, ranked support candidates with matched terms and
coverage, aggregate coverage rate, and an explicit non-verification caveat.
