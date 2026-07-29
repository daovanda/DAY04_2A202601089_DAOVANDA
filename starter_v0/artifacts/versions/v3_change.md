# v3 final routing and capability change

## Evidence behind the change

V2 still called both `lookup` and `social_search` for `M06_switch_tool`, even
though the user explicitly replaced Twitter with web search.

## Hypothesis

Registering the deterministic `evidence_audit` tool adds the team's required
new capability without an external side effect. Exposing optional and competing
tools only for the current task, then suppressing redundant same-tool calls,
will prevent stale/redundant routes while preserving explicit web + social
multi-source requests.

## Iteration evidence

Early v3 candidates regressed because longer negative instructions repeatedly
made `social_search` salient. Those run JSON files are intentionally retained.
The accepted v3 uses the lean v1-style prompt plus runtime task scoping shared
by eval, CLI, and UI. Its accepted base run is:

`runs/v3_B_base_openai_20260729T105820674910.json` (20/20, no provider or tool
execution errors).

## Files

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `tools/__init__.py`
- `tools/evidence_audit/tool.py`
- `tools/evidence_audit/TOOL.md`
- `tools/__init__.py` (`select_relevant_tools`)
- `providers/openai_provider.py` (same-tool deduplication)
