<<<<<<< HEAD
# Research Loop — Day 04 submission

This submission uses OpenAI `gpt-4o-mini` through the Responses API, plus
Tavily, Firecrawl, RapidAPI Twitter, and arXiv tools. The Streamlit UI follows
the design tokens and component rules in the repository-level `DESIGN.md`.

## Environment

Create `.env` in this directory (never commit it):

```dotenv
OPENAI_API_KEY=
=======
# Day 04 Lab v2 — Research Agent

Research Agent đa provider có CLI chat, giao diện Streamlit, eval runner và transcript logging. Bản nộp chính dùng OpenAI `gpt-4o-mini`; adapter Gemini cũng được hỗ trợ. Agent có thể tìm web/X, đọc URL, tìm paper, tạo digest và chạy pipeline kiểm tra bằng chứng.

## Tính năng chính

- Agent loop có lịch sử hội thoại, tool execution và transcript JSON.
- Provider adapters: OpenAI, Gemini, OpenRouter và Anthropic.
- 12 tool được khai báo tập trung trong `artifacts/tools.yaml`.
- 4 tool do nhóm tự viết: `evidence_audit`, `source_deduplicate`, `claim_matrix`, `citation_export`.
- Streamlit UI hiển thị conversation, tool trace, trạng thái và cho tải transcript.
- Eval cho base, group và bonus; artifact được định danh bằng hash prompt/tool.

## Cài đặt

Yêu cầu Python 3.10 trở lên.

```powershell
cd starter_v0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền key cần dùng vào `.env`. Tối thiểu:

```dotenv
OPENAI_API_KEY=
```

Các tool live chỉ cần key tương ứng khi được gọi:

```dotenv
>>>>>>> ae78cb935aa5bf534769cfa89f03d1e1f3e6c13b
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
RAPIDAPI_KEY=
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
<<<<<<< HEAD
ARXIV_USER_AGENT=
```

Install and preflight:

```powershell
python -m pip install -r requirements.txt
python scripts\preflight_provider.py --provider openai --model gpt-4o-mini
```

## Run the product UI
=======
ARXIV_USER_AGENT=AI20k-Day04-Research-Agent/1.0 (educational lab)
```

Telegram là tùy chọn và luôn cần xác nhận trước khi gửi:

```dotenv
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Không commit `.env`. File này đã được `.gitignore`; `.env.example` chỉ chứa tên biến, không chứa secret.

## Chạy ứng dụng

### Streamlit UI
>>>>>>> ae78cb935aa5bf534769cfa89f03d1e1f3e6c13b

```powershell
streamlit run app.py
```

<<<<<<< HEAD
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
=======
Mở `http://localhost:8501`. UI dùng artifact cuối `v3-bonus`, OpenAI và model mặc định `gpt-4o-mini`.

### CLI chat

```powershell
python chat.py --provider openai --version v3-bonus
```

Có thể đổi provider:

```powershell
python chat.py --provider gemini --version v3-bonus
python chat.py --provider openrouter --version v3-bonus
python chat.py --provider anthropic --version v3-bonus
```

Gõ `/exit` hoặc `/quit` để kết thúc. Transcript được lưu trong `transcripts/`.

## Chạy test

```powershell
python -m pytest -q
```

Các test bao phủ audit, ba bonus tool và logic chọn tool theo intent.

## Chạy eval

Base regression:

```powershell
python run_eval.py --phase B --suite base --version v3-bonus --provider openai --eval-cases data/eval_base.json
```

Team-authored group set:

```powershell
python run_eval.py --phase B --suite group --version v3 --provider openai --eval-cases data/eval_group.json
```

Bonus tools:

```powershell
python run_eval.py --phase B --suite bonus --version v3-bonus --provider openai --eval-cases data/eval_bonus.json
```

Một run chỉ hợp lệ để báo cáo khi:

- `provider_error_cases == 0`
- `measured_cases == total_cases`
- các `tool_results` có error đã được review thủ công

## Kết quả được chấp nhận

| Suite | Run | Kết quả |
|---|---|---:|
| Base v0 | `runs/v0_B_base_openai_20260729T102038020359.json` | 16/20 |
| Base v1 | `runs/v1_B_base_openai_20260729T102250058932.json` | 19/20 |
| Base v2 | `runs/v2_B_base_openai_20260729T104026122272.json` | 19/20 |
| Base v3 | `runs/v3_B_base_openai_20260729T105820674910.json` | 20/20 |
| Group v3 | `runs/v3_B_group_openai_20260729T105926703536.json` | 8/10 |
| Bonus v3-bonus | `runs/v3-bonus_B_bonus_openai_20260729T113443811945.json` | 6/6 |
| Base regression v3-bonus | `runs/v3-bonus_B_base_openai_20260729T113625222876.json` | 20/20 |

Tất cả run trong bảng có `provider_error_cases=0`.

## Cấu trúc

```text
starter_v0/
├── app.py                  # Streamlit UI
├── agent.py                # Single-pass agent dùng cho eval
├── chat.py                 # Interactive agent loop
├── run_eval.py             # Eval runner
├── providers/              # Provider adapters
├── tools/                  # Tool implementations + TOOL.md
├── artifacts/
│   ├── system_prompt.md
│   ├── tools.yaml
│   ├── REPORT.md
│   └── versions/           # Lịch sử v0 → v3-bonus
├── data/                   # Base/group/bonus eval sets
├── tests/                  # Unit/regression tests
├── runs/                   # Machine-readable eval evidence
├── transcripts/            # CLI/UI live-chat evidence
└── analysis/all_runs.csv   # Phân tích tổng hợp
```

## Tài liệu nộp bài

- Báo cáo đầy đủ: `artifacts/REPORT.md`
- System prompt cuối: `artifacts/system_prompt.md`
- Tool declarations: `artifacts/tools.yaml`
- Lịch sử metric: `artifacts/version_log.csv`
- Thay đổi bonus: `artifacts/versions/v3_bonus_change.md`

## Lưu ý an toàn

- Không đưa API key, bot token hoặc chat ID vào source, transcript hay ảnh chụp.
- Rotate ngay credential nếu từng xuất hiện trong chat, log hoặc commit.
- `send` là side-effect tool: chỉ gọi sau xác nhận rõ ràng.
- `claim_matrix` chỉ gợi ý nguồn theo lexical overlap, không xác minh claim.
- `citation_export` không bịa metadata còn thiếu.
>>>>>>> ae78cb935aa5bf534769cfa89f03d1e1f3e6c13b
