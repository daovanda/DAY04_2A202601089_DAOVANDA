# evidence_audit

## Purpose

Audit a list of collected research items before synthesis or publication. The
tool checks whether evidence exists, comes from enough distinct sources, has
valid citation URLs, avoids duplicate URLs, and contains usable text.

This is the team's new mandatory tool. It is deterministic and does not call an
external service.

## Use when

- The user asks to verify, audit, or quality-check sources/evidence already
  present in the conversation.
- A research digest should be checked for citation coverage or source diversity
  before publication.

## Do not use when

- No source items have been collected yet; first use a retrieval tool.
- The user is asking to find new information. This tool evaluates items but
  does not retrieve them.
- The user only asks to format results.

## Arguments

- `items` (required): research items containing `title` or `summary`, `url`, and
  optionally `source`.
- `min_sources` (default `2`): minimum distinct domains/accounts required.
- `require_urls` (default `true`): whether every item must have an HTTP(S)
  citation URL.

## Output

Returns an overall score and pass flag, per-check booleans, detected issue
indexes/URLs, and actionable recommendations. It never modifies or publishes
the provided data.
