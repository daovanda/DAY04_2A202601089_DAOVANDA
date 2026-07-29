# Research Loop — Day 04 submission

This submission uses OpenAI `gpt-4o-mini` through the Responses API, plus
Tavily, Firecrawl, RapidAPI Twitter, and arXiv tools. The Streamlit UI follows
the design tokens and component rules in the repository-level `DESIGN.md`.

## Environment

Create `.env` in this directory (never commit it):

```dotenv
OPENAI_API_KEY=
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
RAPIDAPI_KEY=
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
ARXIV_USER_AGENT=
```

Install and preflight:

```powershell
python -m pip install -r requirements.txt
python scripts\preflight_provider.py --provider openai --model gpt-4o-mini
```

## Run the product UI

```powershell
streamlit run app.py
```

Open `http://localhost:8501`. The UI includes:

- live multi-round chat using the same `run_model_tool_loop` as the CLI;
- tool timeline with round, name, arguments, status, result, and errors;
- transcript download and artifact-version identifiers;
- run metrics and the same scenario compared across v0–v3 plus the bonus artifact;
- the complete tool declaration catalog.

`streamlit run` intentionally stays active until stopped. Press `Ctrl+C` in its
terminal to shut the local server down.

## Reproduce evals

```powershell
python run_eval.py --provider openai --model gpt-4o-mini --version v3 --suite base --eval-cases data\eval_base.json
python run_eval.py --provider openai --model gpt-4o-mini --version v3 --suite group --eval-cases data\eval_group.json
python run_eval.py --provider openai --model gpt-4o-mini --version v3-bonus --suite bonus --eval-cases data\eval_bonus.json
python scripts\parse_runs.py runs --output analysis\all_runs.csv
```

Eval commands execute real tools. Keep Telegram credentials unset unless a
confirmed live-send demo is explicitly intended.

## Team-authored capability

`evidence_audit` is the new deterministic tool in
`tools/evidence_audit/`. It checks source diversity, citation URLs,
duplicates, and missing content before synthesis/publication. It has a
dedicated `TOOL.md` and unit tests in `tests/test_evidence_audit.py`.

The completed bonus track adds three more team-authored tools:

- `source_deduplicate`: canonical URL/title duplicate removal;
- `claim_matrix`: claim-to-source candidate coverage;
- `citation_export`: Markdown, APA-like, and BibTeX export.

Their six dedicated eval cases are in `data/eval_bonus.json`; direct behavior
tests are in `tests/test_bonus_tools.py`.
