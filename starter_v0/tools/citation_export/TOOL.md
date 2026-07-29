# citation_export

## Purpose

Export collected source items as Markdown references, APA-like references, or
BibTeX records after research is complete.

This is a team-authored bonus tool. It is deterministic, read-only, and does
not retrieve metadata or invent missing authors/dates.

## Use when

- The user asks to export citations, references, a bibliography, APA-like
  entries, Markdown links, or BibTeX from source items already present.

## Do not use when

- Sources have not been collected yet.
- Duplicate cleanup or source-quality auditing is requested.
- The user expects authoritative publisher metadata not present in the items.

## Arguments

- `items` (required): source objects with title plus optional URL, authors,
  source, date/published/year, and summary.
- `style`: `markdown` (default), `apa`, or `bibtex`.
- `include_abstract`: append source summary/note when available.

## Output

Returns individual `citations`, their count, selected style, and a joined
`text` block ready to copy. Missing metadata remains visibly generic rather
than being fabricated.
