from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
FINAL_VERSION = "v3-bonus"
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Loop — Evidence-first agent",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_design_system() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        :root {
          --canvas:#f7f7f4; --canvas-soft:#fafaf7; --card:#fff;
          --ink:#26251e; --body:#5a5852; --muted:#807d72;
          --hairline:#e6e5e0; --hairline-strong:#cfcdc4;
          --orange:#f54e00; --orange-active:#d04200;
          --thinking:#dfa88f; --grep:#9fc9a2; --read:#9fbbe0;
          --edit:#c0a8dd; --done:#c08532; --success:#1f8a65; --error:#cf2d56;
        }
        html, body, [class*="css"], .stApp {
          font-family: Inter, system-ui, sans-serif;
          color: var(--ink);
        }
        .stApp { background: var(--canvas); }
        .block-container { max-width: 1200px; padding: 24px 32px 80px; }
        header[data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer { visibility: hidden; }
        h1, h2, h3 { font-weight: 400 !important; letter-spacing: -0.025em; color: var(--ink); }
        p, label, .stCaption { color: var(--body); }
        code, pre, [data-testid="stJson"] {
          font-family: "JetBrains Mono", monospace !important; font-size: 13px;
        }
        .top-nav {
          min-height:64px; display:flex; align-items:center; justify-content:space-between;
          border-bottom:1px solid var(--hairline); margin-bottom:48px;
        }
        .brand { font-size:16px; font-weight:600; color:var(--orange); letter-spacing:-.02em; }
        .nav-meta { font:11px "JetBrains Mono",monospace; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }
        .hero { padding:28px 0 48px; max-width:900px; }
        .eyebrow { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
        .hero h1 { font-size:clamp(38px,6vw,72px); line-height:1.06; margin:14px 0 18px; }
        .hero p { max-width:680px; font-size:17px; line-height:1.55; }
        .version-strip {
          display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-top:24px;
        }
        .chip {
          display:inline-flex; align-items:center; min-height:28px; padding:4px 10px;
          border-radius:9999px; background:#e6e5e0; color:var(--ink);
          font:600 11px/1.4 "JetBrains Mono",monospace; text-transform:uppercase; letter-spacing:.06em;
        }
        .chip.live { background:var(--orange); color:white; }
        .section-label { margin:42px 0 14px; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
        .surface, div[data-testid="stForm"], div[data-testid="stExpander"] {
          background:var(--card); border:1px solid var(--hairline) !important;
          border-radius:12px !important; box-shadow:none !important;
        }
        .metric-card { background:var(--card); border:1px solid var(--hairline); border-radius:12px; padding:20px; min-height:120px; }
        .metric-card .value { font-size:30px; letter-spacing:-.04em; color:var(--ink); margin:8px 0 4px; }
        .metric-card .label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
        .metric-card .sub { font:12px "JetBrains Mono",monospace; color:var(--body); }
        div[data-testid="stChatMessage"] {
          background:var(--card); border:1px solid var(--hairline); border-radius:12px;
          padding:4px 8px; box-shadow:none;
        }
        div[data-testid="stChatInput"] { border-color:var(--hairline-strong); border-radius:8px; background:var(--card); }
        .stButton > button, .stDownloadButton > button {
          border-radius:8px; min-height:40px; border:1px solid var(--hairline-strong);
          background:var(--card); color:var(--ink); box-shadow:none; font-weight:500;
        }
        .stButton > button[kind="primary"] { background:var(--orange); color:#fff; border-color:var(--orange); }
        .stButton > button[kind="primary"]:active { background:var(--orange-active); }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
          background:var(--card); border-color:var(--hairline-strong); border-radius:8px; box-shadow:none;
        }
        .trace {
          background:var(--canvas-soft); border:1px solid var(--hairline);
          border-radius:8px; padding:14px 16px; margin:8px 0;
        }
        .trace-head { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
        .trace-title { font:500 13px "JetBrains Mono",monospace; }
        .timeline-pill {
          border-radius:9999px; padding:4px 10px; color:var(--ink);
          font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.08em;
        }
        .timeline-pill.thinking { background:var(--thinking); }
        .timeline-pill.read { background:var(--read); }
        .timeline-pill.edit { background:var(--edit); }
        .timeline-pill.done { background:var(--done); color:white; }
        .timeline-pill.error { background:transparent; color:var(--error); border:1px solid var(--error); }
        .trace pre { white-space:pre-wrap; word-break:break-word; margin:0; color:var(--body); }
        .empty-state { padding:36px; text-align:center; border:1px dashed var(--hairline-strong); border-radius:12px; color:var(--muted); }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:24px; border-bottom:1px solid var(--hairline); }
        div[data-testid="stTabs"] button { background:transparent; }
        @media (max-width:640px) {
          .block-container { padding:16px 16px 64px; }
          .top-nav { margin-bottom:24px; }
          .nav-meta { display:none; }
          .hero { padding:20px 0 32px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def make_transcript_id(version: str) -> str:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return f"{version}_openai_ui_{stamp}"


def reset_conversation(version: str, artifact: dict[str, str], model: str) -> None:
    transcript_id = make_transcript_id(version)
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact,
        "provider": "openai",
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def load_runs() -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for path in sorted(RUNS_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["_path"] = path
            payloads.append(payload)
        except (OSError, json.JSONDecodeError):
            continue
    return payloads


def metric_card(label: str, value: Any, sub: str = "") -> None:
    shown = "—" if value is None else value
    if isinstance(shown, float):
        shown = f"{shown * 100:.1f}%"
    st.markdown(
        f'<div class="metric-card"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(str(shown))}</div>'
        f'<div class="sub">{html.escape(sub)}</div></div>',
        unsafe_allow_html=True,
    )


def render_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds", [])
    if not rounds:
        return
    with st.expander(f"Agent timeline · {len(rounds)} round(s)", expanded=False):
        for round_data in rounds:
            calls = round_data.get("tool_calls", [])
            if not calls:
                st.markdown(
                    '<div class="trace"><div class="trace-head">'
                    '<span class="timeline-pill done">Done</span>'
                    f'<span class="trace-title">round {round_data.get("round")}</span></div>'
                    '<pre>No tool call · final response composed</pre></div>',
                    unsafe_allow_html=True,
                )
                continue
            for index, call in enumerate(calls):
                result_event = (round_data.get("tool_results") or [{}])[index] if index < len(round_data.get("tool_results") or []) else {}
                result = result_event.get("result", {})
                has_error = isinstance(result, dict) and bool(result.get("error"))
                status_class = "error" if has_error else "read"
                status_text = "Error" if has_error else "Reading"
                args_text = json.dumps(call.get("args", {}), ensure_ascii=False, indent=2)
                result_text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
                if len(result_text) > 3500:
                    result_text = result_text[:3500] + "\n…<truncated>"
                st.markdown(
                    '<div class="trace"><div class="trace-head">'
                    f'<span class="timeline-pill {status_class}">{status_text}</span>'
                    f'<span class="trace-title">round {round_data.get("round")} · {html.escape(call.get("name", ""))}</span>'
                    '</div><pre>'
                    f'ARGS\n{html.escape(args_text)}\n\nRESULT\n{html.escape(result_text)}'
                    '</pre></div>',
                    unsafe_allow_html=True,
                )


inject_design_system()

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
declarations = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(declarations)
artifact_obj = build_artifact_version(FINAL_VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH)
artifact = artifact_version_dict(artifact_obj)
default_model = getattr(make_provider("openai"), "default_model", "gpt-4o-mini")

if "transcript" not in st.session_state:
    reset_conversation(FINAL_VERSION, artifact, default_model)

st.markdown(
    '<div class="top-nav"><div class="brand">research/loop</div>'
    '<div class="nav-meta">Evidence-first agent · Day 04 lab</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<section class="hero"><div class="eyebrow">Research agent workspace</div>'
    '<h1>Research you can inspect,<br>not just trust.</h1>'
    '<p>Search the web and social feeds, read sources, inspect every tool decision, '
    'and compare how routing improves across prompt versions.</p>'
    f'<div class="version-strip"><span class="chip live">OpenAI live</span>'
    f'<span class="chip">{html.escape(artifact["artifact_version"])}</span>'
    f'<span class="chip">{len(declarations)} tools</span></div></section>',
    unsafe_allow_html=True,
)

chat_tab, evidence_tab, tools_tab = st.tabs(["Workspace", "Version evidence", "Tool catalog"])

with chat_tab:
    controls, workspace = st.columns([0.31, 0.69], gap="large")
    with controls:
        st.markdown('<div class="section-label">Session controls</div>', unsafe_allow_html=True)
        model = st.text_input("OpenAI model", value=default_model, help="Leave the default unless your API plan requires another model.")
        max_rounds = st.select_slider("Maximum tool rounds", options=[1, 2, 3, 4, 5, 6], value=4)
        st.caption(f"Transcript: {st.session_state.transcript['transcript_id']}")
        if st.button("New conversation", use_container_width=True):
            reset_conversation(FINAL_VERSION, artifact, model)
            st.rerun()
        if st.session_state.transcript_path.exists():
            st.download_button(
                "Download transcript",
                data=st.session_state.transcript_path.read_bytes(),
                file_name=st.session_state.transcript_path.name,
                mime="application/json",
                use_container_width=True,
            )

        st.markdown('<div class="section-label">Try a scenario</div>', unsafe_allow_html=True)
        examples = [
            "Tin AI hôm nay có gì nổi bật?",
            "Tìm trên web tin robotics tuần này và tweet top về robotics.",
            "Tóm tắt 5 tweet mới nhất giúp mình.",
            "Tóm tắt bài này: https://openai.com/news/",
            "Tìm paper mới về retrieval-augmented generation.",
        ]
        for example in examples:
            st.caption(f"→ {example}")

    with workspace:
        st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
        if not st.session_state.turns:
            st.markdown(
                '<div class="empty-state">Ask a research question. Each answer will keep its '
                'rounds, tool arguments, result status, and artifact version.</div>',
                unsafe_allow_html=True,
            )
        for turn in st.session_state.turns:
            with st.chat_message("user"):
                st.markdown(turn["user"])
            with st.chat_message("assistant"):
                if turn.get("status") == "provider_error":
                    st.error(turn.get("error", "Provider error"))
                else:
                    st.markdown(turn.get("assistant_text") or "_No text response._")
                render_trace(turn)

        user_text = st.chat_input("Ask the research agent…")
        if user_text:
            turn_record: dict[str, Any] = {
                "turn_index": len(st.session_state.turns) + 1,
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            try:
                provider = make_provider("openai")
                messages = [
                    {"role": "system", "content": system_prompt},
                    *trim_history(st.session_state.history, 5),
                    {"role": "user", "content": user_text},
                ]
                with st.spinner("Researching and recording evidence…"):
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=model or None,
                        max_tool_rounds=max_rounds,
                    )
                turn_record.update(result)
                st.session_state.history.extend([
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": result["assistant_text"]},
                ])
            except Exception as exc:
                turn_record.update({
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {exc}",
                })
            turn_record["ended_at"] = now_iso()
            st.session_state.turns.append(turn_record)
            st.session_state.transcript["turns"] = st.session_state.turns
            st.session_state.transcript["model"] = model or default_model
            write_transcript(st.session_state.transcript_path, st.session_state.transcript)
            st.rerun()

with evidence_tab:
    st.markdown('<div class="section-label">Measured runs</div>', unsafe_allow_html=True)
    runs = load_runs()
    if not runs:
        st.markdown('<div class="empty-state">No eval run JSON is available yet.</div>', unsafe_allow_html=True)
    else:
        labels = [
            f"{run.get('version')} · {run.get('suite')} · {run.get('generated_at')} · {run['_path'].name}"
            for run in runs
        ]
        selected_label = st.selectbox("Run", labels)
        selected_run = runs[labels.index(selected_label)]
        summary = selected_run.get("summary", {})
        cols = st.columns(4)
        with cols[0]:
            metric_card("Case accuracy", summary.get("case_accuracy"), f"{summary.get('passed_cases', 0)}/{summary.get('measured_cases', 0)} measured")
        with cols[1]:
            metric_card("Tool routing", summary.get("tool_routing_accuracy"), "correct tool selection")
        with cols[2]:
            metric_card("Argument accuracy", summary.get("argument_accuracy"), "expected argument subset")
        with cols[3]:
            metric_card("Provider errors", summary.get("provider_error_cases"), f"{summary.get('total_cases', 0)} total cases")
        st.caption(f"Artifact version: {selected_run.get('artifact_version')} · Model: {selected_run.get('model')}")

        rows = []
        for item in selected_run.get("results", []):
            result = item.get("result", {})
            rows.append({
                "case": item.get("id"),
                "status": "PASS" if result.get("passed") else "FAIL",
                "expected failure class": item.get("metadata", {}).get("what_it_tests") or result.get("case_failure_type"),
                "observed mismatch": result.get("observed_mismatch"),
                "tool calls": ", ".join(call.get("name", "") for call in result.get("actual_tool_calls", [])) or "—",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-label">Same scenario across versions</div>', unsafe_allow_html=True)
        latest_by_version: dict[str, dict[str, Any]] = {}
        for run in runs:
            if run.get("provider") != "openai" or run.get("suite") != "base":
                continue
            version = str(run.get("version", ""))
            if version and version not in latest_by_version:
                latest_by_version[version] = run
        case_ids = sorted({
            str(item.get("id"))
            for run in latest_by_version.values()
            for item in run.get("results", [])
            if item.get("id")
        })
        if case_ids:
            default_case = "M06_switch_tool" if "M06_switch_tool" in case_ids else case_ids[0]
            compare_case = st.selectbox(
                "Scenario to compare",
                case_ids,
                index=case_ids.index(default_case),
            )
            comparison_rows = []
            for version in sorted(latest_by_version):
                run = latest_by_version[version]
                item = next(
                    (entry for entry in run.get("results", []) if entry.get("id") == compare_case),
                    None,
                )
                if not item:
                    continue
                result = item.get("result", {})
                call_summary = "; ".join(
                    f"{call.get('name')}({json.dumps(call.get('args', {}), ensure_ascii=False, sort_keys=True)})"
                    for call in result.get("actual_tool_calls", [])
                ) or "no tool"
                comparison_rows.append({
                    "version": version,
                    "status": "PASS" if result.get("passed") else "FAIL",
                    "actual route": call_summary,
                    "observed mismatch": result.get("observed_mismatch") or "—",
                    "artifact version": run.get("artifact_version"),
                })
            st.dataframe(comparison_rows, use_container_width=True, hide_index=True)

        with st.expander("Inspect raw run JSON"):
            st.json({key: value for key, value in selected_run.items() if key != "_path"}, expanded=False)

with tools_tab:
    st.markdown('<div class="section-label">Declared capability surface</div>', unsafe_allow_html=True)
    st.markdown("### Tools are part of the prompt")
    st.caption("Names and descriptions define the routing interface. Sensitive credentials are never rendered here.")
    for declaration in declarations:
        properties = declaration.get("parameters", {}).get("properties", {})
        required = set(declaration.get("parameters", {}).get("required", []))
        with st.expander(declaration["name"]):
            st.write(declaration.get("description", ""))
            st.code(
                "\n".join(
                    f"{name}{' *' if name in required else ''}: {schema.get('type', 'any')}"
                    for name, schema in properties.items()
                ) or "No arguments",
                language="text",
            )
