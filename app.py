import json
import os
import re
import subprocess
import sys
import ast
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PatchBot AI | Autonomous Cyber-Remediation Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CUSTOM CYBER-SECURITY GLASSMORPHISM & HERO CSS ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #060913;
    color: #e2e8f0;
}

.stApp {
    background:
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.14), transparent 35%),
        radial-gradient(circle at 85% 20%, rgba(168, 85, 247, 0.14), transparent 35%),
        linear-gradient(rgba(30, 41, 59, 0.25) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30, 41, 59, 0.25) 1px, transparent 1px),
        #060913;
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px, 100% 100%;
}

/* Hero Landing Banner */
.hero-box {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(17, 24, 39, 0.92));
    border: 1px solid rgba(56, 189, 248, 0.35);
    box-shadow: 0 0 40px rgba(56, 189, 248, 0.12), inset 0 1px 0 rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2.6rem 2.8rem;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(14px);
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 1rem;
}

.cyber-pill {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #7dd3fc;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.cyber-pill.purple {
    background: rgba(168, 85, 247, 0.12);
    border-color: rgba(168, 85, 247, 0.45);
    color: #d8b4fe;
}

.cyber-pill.green {
    background: rgba(16, 185, 129, 0.12);
    border-color: rgba(16, 185, 129, 0.45);
    color: #6ee7b7;
}

.hero-title {
    font-size: 2.85rem;
    font-weight: 800;
    line-height: 1.12;
    margin: 0.2rem 0 0.7rem 0;
    background: linear-gradient(90deg, #ffffff 0%, #38bdf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.08rem;
    color: #94a3b8;
    max-width: 820px;
    line-height: 1.6;
}

/* Architecture Cards */
.arch-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 16px;
    padding: 1.25rem;
    height: 100%;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.arch-card:hover {
    border-color: rgba(56, 189, 248, 0.55);
    transform: translateY(-2px);
}
.arch-step {
    font-size: 0.72rem;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.arch-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0.25rem 0 0.4rem 0;
}
.arch-desc {
    font-size: 0.86rem;
    color: #94a3b8;
    line-height: 1.45;
}

/* KPI Metric Cards */
.kpi-card {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.65));
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    text-align: left;
}
.kpi-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}
.kpi-val {
    font-size: 1.85rem;
    font-weight: 800;
    color: #f8fafc;
    margin-top: 0.2rem;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #34d399;
    margin-top: 0.15rem;
}

/* Terminal Window */
.terminal-header {
    background: #0f172a;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-bottom: none;
    border-radius: 12px 12px 0 0;
    padding: 0.55rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #94a3b8;
    display: flex;
    justify-content: space-between;
}

/* Primary Launch Button */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #0284c7, #7c3aed);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.35);
    transition: all 0.2s ease;
    width: 100%;
}
div.stButton > button:first-child:hover {
    box-shadow: 0 10px 30px rgba(56, 189, 248, 0.5);
    transform: translateY(-1px);
}
</style>
""",
    unsafe_allow_html=True,
)

# --- HERO LANDING SECTION ---
st.markdown(
    """
<div class="hero-box">
    <div class="pill-row">
        <span class="cyber-pill">● Autonomous Self-Healing Engine</span>
        <span class="cyber-pill purple">LangGraph Multi-Agent Orchestration</span>
        <span class="cyber-pill green">Docker Ephemeral Sandbox</span>
    </div>
    <div class="hero-title">PatchBot AI — Autonomous Code & Vulnerability Remediation</div>
    <div class="hero-sub">
        Detects critical security flaws, synthesizes verified AST-safe patches via Gemini AI,
        stress-tests fixes inside isolated Docker containers, and deploys production-ready
        GitHub Pull Requests with zero human intervention.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 4-STAGE ARCHITECTURE PIPELINE ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        """<div class="arch-card">
        <div class="arch-step">Stage 01 • Reason</div>
        <div class="arch-name">🧠 Planner Agent</div>
        <div class="arch-desc">Inspects vulnerable AST patterns (e.g., unsafe <code>eval()</code> injection) and synthesizes a minimal secure patch.</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """<div class="arch-card">
        <div class="arch-step">Stage 02 • Isolate</div>
        <div class="arch-name">🐳 Docker Sandbox</div>
        <div class="arch-desc">Spins up an ephemeral <code>python:3.11-slim</code> container and isolated Git worktree to contain untrusted execution.</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """<div class="arch-card">
        <div class="arch-step">Stage 03 • Verify</div>
        <div class="arch-name">🛡️ Hostile Evaluator</div>
        <div class="arch-desc">Runs automated unit & exploit test suites. Routes failures back to Planner in a self-healing reflection loop.</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        """<div class="arch-card">
        <div class="arch-step">Stage 04 • Ship</div>
        <div class="arch-name">🚀 GitHub PR Gate</div>
        <div class="arch-desc">Commits verified patch to a clean branch, opens a live Pull Request with audit report, and destroys container artifacts.</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- LOAD BENCHMARK METRICS ---
metrics_data = []
if os.path.exists("benchmark_metrics.json"):
    try:
        with open("benchmark_metrics.json", "r") as f:
            metrics_data = json.load(f)
    except Exception:
        metrics_data = []

if metrics_data:
    df = pd.DataFrame(metrics_data)
    total_runs = len(df)
    pass_rate = (df["resolved"].sum() / total_runs) * 100 if "resolved" in df else 100.0
    avg_time = df["execution_time_sec"].mean() if "execution_time_sec" in df else 0.0
    avg_rev = df["revisions_needed"].mean() if "revisions_needed" in df else 1.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Autonomous Resolution Rate</div><div class="kpi-val">{pass_rate:.0f}%</div><div class="kpi-sub">✓ Verified via Docker Exit Code 0</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Mean Time to Patch</div><div class="kpi-val">{avg_time:.1f}s</div><div class="kpi-sub">⚡ End-to-End Sandbox + PR</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Self-Healing Loop Avg</div><div class="kpi-val">{avg_rev:.1f}x</div><div class="kpi-sub">↻ Iterative Planner-Evaluator Cycles</div></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Benchmarked CVE Drills</div><div class="kpi-val">{total_runs}</div><div class="kpi-sub">🔒 Zero-Leak Ephemeral Worktrees</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)

# --- INTERACTIVE TABS ---
tab_live, tab_bench, tab_code = st.tabs(
    ["⚡ Live Autonomous Remediation Console", "📊 Benchmark Analytics", "🔍 Target Vulnerability Inspector"]
)

with tab_live:
    left_col, right_col = st.columns([1, 2.2])

    with left_col:
        st.markdown("#### Mission Control")
        st.markdown(
            "Trigger a live end-to-end fire drill against `calculator.py` (`eval()` Remote Code Execution vulnerability)."
        )
        run_clicked = st.button("🚀 Launch Live Autonomous Patch")

        st.markdown("---")
        st.markdown("**Active Environment**")
        st.code(
            f"Repo: riyasingh1102345/Patchbot\nModel: gemini-3.5-flash-lite\nSandbox: python:3.11-slim\nRuntime: {os.path.basename(sys.executable)}",
            language="yaml",
        )
        st.link_button(
            "🔗 Open GitHub Pull Requests",
            "https://github.com/riyasingh1102345/Patchbot/pulls",
            use_container_width=True,
        )

    with right_col:
        st.markdown(
            '<div class="terminal-header"><span>● PATCHBOT-CORE // LIVE TELEMETRY STREAM</span><span>UTF-8 • DOCKER-MCP</span></div>',
            unsafe_allow_html=True,
        )
        log_box = st.empty()
        pr_banner = st.empty()

        if run_clicked:
            logs = "Initializing LangGraph State Machine & Docker MCP Client...\n"
            log_box.code(logs, language="text")

            # Use sys.executable so it runs inside .venv with dotenv & langgraph installed!
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            process = subprocess.Popen(
                [sys.executable, "-u", "run_patchbot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )

            pr_url = None
            for line in process.stdout:
                logs += line
                log_box.code(logs, language="text")
                match = re.search(r"https://github\.com/[^\s]+/pull/\d+", line)
                if match:
                    pr_url = match.group(0)

            process.wait()

            if process.returncode == 0:
                st.balloons()
                if pr_url:
                    pr_banner.success(f"🎉 Vulnerability Patched & Verified! Live Pull Request Deployed: {pr_url}")
                    st.link_button("🌐 Inspect Live GitHub PR & Code Diff", pr_url, type="primary")
                else:
                    pr_banner.success("🎉 Autonomous Remediation Pipeline Completed Successfully!")
            else:
                pr_banner.error(f"Pipeline halted with exit code {process.returncode}. Review trace above.")
        else:
            log_box.code(
                "System Armed & Ready.\nClick '🚀 Launch Live Autonomous Patch' on the left to execute the live multi-agent healing loop.",
                language="text",
            )

with tab_bench:
    if metrics_data:
        st.markdown("#### Execution Latency & Revision Convergence Across Runs")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.caption("Execution Time per Run (Seconds)")
            st.bar_chart(df.set_index("run_id")["execution_time_sec"], color="#38bdf8")
        with chart_col2:
            st.caption("Output Tokens Generated per Patch")
            st.bar_chart(df.set_index("run_id")["output_tokens"], color="#a855f7")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No `benchmark_metrics.json` records found yet.")

with tab_code:
    st.markdown("#### Target Source (`app.py`)")
    if os.path.exists("app.py"):
        with open("app.py", "r") as f:
            st.code(f.read(), language="python")