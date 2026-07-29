# source_deduplicate

## Purpose

Remove repeated research-source items before audit, synthesis, or citation
export. It canonicalizes URLs, removes common tracking parameters, and can fall
back to normalized titles when a URL is missing.

This is a team-authored bonus tool. It is deterministic, read-only, and makes
no network request.

## Use when

- The user asks to deduplicate, de-duplicate, remove repeated sources, or merge
  a source list containing duplicate URLs/titles.
- Retrieved items should be cleaned before `evidence_audit`,
  `claim_matrix`, or `citation_export`.

## Do not use when

- The user wants to search for new sources.
- The user asks whether sources are trustworthy; use `evidence_audit`.
- The user only wants output formatting.

## Arguments

- `items` (required): source objects; `url` and `title` are used as keys.
- `strategy`: `url`, `title`, or `url_or_title` (default).
- `preserve_order`: retain first-seen input order (default `true`).

## Output

Returns `unique_items`, counts, and `duplicate_groups` with kept/removed input
indexes so the transformation remains auditable.
