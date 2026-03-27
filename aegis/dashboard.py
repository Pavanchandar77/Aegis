"""
AEGIS — Premium Fintech Dashboard
Hackathon-winning UI with dramatic trade blocking visuals.
"""

import streamlit as st
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AEGIS Risk Governor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREMIUM DARK THEME CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');

    /* ── Global Dark Theme ── */
    .stApp {
        background: #0b0f19;
        color: #e0e6ed;
    }
    header[data-testid="stHeader"] {
        background: #0b0f19;
    }
    section[data-testid="stSidebar"] {
        background: #0d1220;
    }

    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    p, span, li, div {
        font-family: 'Inter', sans-serif;
    }

    /* ── Cards ── */
    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #1a1f36 100%);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 30px rgba(59,130,246,0.15);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #f8fafc;
    }
    .metric-value.green { color: #10b981; }
    .metric-value.red { color: #ef4444; }
    .metric-value.blue { color: #3b82f6; }
    .metric-value.amber { color: #f59e0b; }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 20px;
        padding: 40px 48px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(59,130,246,0.08) 0%, transparent 50%);
    }
    .hero-title {
        font-size: 42px;
        font-weight: 900;
        letter-spacing: -1px;
        margin: 0;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
    }
    .hero-sub {
        font-size: 16px;
        color: #94a3b8;
        margin-top: 8px;
        position: relative;
    }

    /* ── Decision Panels ── */
    .decision-executed {
        background: linear-gradient(135deg, #052e16 0%, #064e3b 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 0 40px rgba(16,185,129,0.15);
    }
    .decision-blocked {
        background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        animation: pulseRed 2s ease-in-out infinite;
        box-shadow: 0 0 60px rgba(239,68,68,0.3);
    }
    .decision-hold {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #475569;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
    }
    .decision-text {
        font-size: 36px;
        font-weight: 900;
        font-family: 'Inter', sans-serif;
        letter-spacing: 2px;
    }
    .decision-reason {
        font-size: 15px;
        color: #fca5a5;
        margin-top: 12px;
        font-weight: 500;
    }
    .capital-saved {
        font-size: 14px;
        color: #10b981;
        margin-top: 16px;
        padding: 10px 20px;
        background: rgba(16,185,129,0.1);
        border-radius: 8px;
        display: inline-block;
        font-weight: 600;
    }

    @keyframes pulseRed {
        0%, 100% { box-shadow: 0 0 30px rgba(239,68,68,0.2); }
        50% { box-shadow: 0 0 80px rgba(239,68,68,0.5), 0 0 120px rgba(239,68,68,0.1); }
    }

    /* ── Section Headers ── */
    .section-header {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #3b82f6;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e293b;
    }

    /* ── Log Entries ── */
    .log-entry {
        background: #111827;
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 6px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .log-entry.blocked {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, #1c0a0a 0%, #111827 30%);
    }
    .log-entry.executed {
        border-left-color: #10b981;
    }

    /* ── Volatility Badge ── */
    .vol-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .vol-low { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid #10b981; }
    .vol-med { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid #f59e0b; }
    .vol-high { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid #ef4444; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
        padding: 10px 24px;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        border: none !important;
    }

    /* ── Remove default padding ── */
    .block-container { padding-top: 2rem; }

    /* ── Plotly dark ── */
    .js-plotly-plot .plotly .modebar { display: none !important; }

    /* ── Streamlit metric override ── */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 28px !important;
        color: #f8fafc !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 11px !important;
    }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def api(endpoint: str, method: str = "GET"):
    try:
        if method == "POST":
            r = requests.post(f"{API_URL}{endpoint}", timeout=10)
        else:
            r = requests.get(f"{API_URL}{endpoint}", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def plotly_dark(fig, height=350):
    fig.update_layout(
        plot_bgcolor="#0b0f19",
        paper_bgcolor="#0b0f19",
        font=dict(family="Inter", color="#94a3b8"),
        height=height,
        margin=dict(t=20, b=40, l=50, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        xaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">AEGIS</div>
    <div class="hero-sub">Autonomous Risk Governor &mdash; AI-powered trade firewall that blocks dangerous trades in real-time</div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTROL BAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1.5])

with c1:
    demo_clicked = st.button("🚀  RUN DEMO SCENARIO", use_container_width=True, type="primary")
with c2:
    cycle_clicked = st.button("▶  Run Single Cycle", use_container_width=True)
with c3:
    vol_on = st.button("⚡  Volatility Spike", use_container_width=True)
with c4:
    reset_clicked = st.button("🔄  Reset System", use_container_width=True)
with c5:
    auto_run = st.toggle("Auto", value=False, help="Auto-run cycles every 1.5s")

# Handle button actions
if demo_clicked:
    with st.spinner("Running demo scenario..."):
        demo_result = api("/demo-scenario", "POST")
    if "error" not in demo_result:
        st.session_state["demo_result"] = demo_result
if cycle_clicked:
    api("/run-cycle", "POST")
if vol_on:
    api("/set-volatile?volatile=true", "POST")
if reset_clicked:
    api("/reset", "POST")
    st.session_state.pop("demo_result", None)
    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FETCH DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
status = api("/status")
if "error" in status:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:64px; margin-bottom:20px;">🛡️</div>
        <div style="font-size:24px; color:#ef4444; font-weight:700;">AEGIS API Offline</div>
        <div style="color:#64748b; margin-top:12px;">
            Start the API server first:<br>
            <code style="color:#3b82f6;">python -m aegis.api</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

logs_data = api("/logs?last_n=50")
logs = logs_data.get("logs", [])
latest = logs[-1] if logs else None
threshold = status.get("risk_threshold", 0.65)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KEY METRICS ROW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
price = status.get("current_price", 0) or 0
vol = status.get("volatility", 0) or 0
vol_pct = vol * 100

if vol_pct > 2.0:
    vol_badge = '<span class="vol-badge vol-high">EXTREME</span>'
elif vol_pct > 0.8:
    vol_badge = '<span class="vol-badge vol-med">ELEVATED</span>'
else:
    vol_badge = '<span class="vol-badge vol-low">NORMAL</span>'

m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">BTC / USDT</div>
        <div class="metric-value blue">${price:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Volatility</div>
        <div class="metric-value {'red' if vol_pct > 2 else 'amber' if vol_pct > 0.8 else 'green'}">{vol_pct:.2f}%</div>
        <div style="margin-top:8px;">{vol_badge}</div>
    </div>""", unsafe_allow_html=True)

with m3:
    pnl = status.get("pnl", 0) or 0
    pnl_class = "green" if pnl >= 0 else "red"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Portfolio P&L</div>
        <div class="metric-value {pnl_class}">{"+" if pnl >= 0 else ""}${pnl:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with m4:
    pv = status.get("portfolio_value", 100000) or 100000
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Portfolio Value</div>
        <div class="metric-value">${pv:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with m5:
    blocked = status.get("trades_blocked", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Trades Blocked</div>
        <div class="metric-value red">{blocked}</div>
    </div>""", unsafe_allow_html=True)

with m6:
    approved = status.get("trades_approved", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Trades Approved</div>
        <div class="metric-value green">{approved}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN: DECISION + RISK GAUGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if latest:
    col_decision, col_gauge, col_strategy = st.columns([2, 1.5, 1.5])

    # ── Decision Panel ──
    with col_decision:
        st.markdown('<div class="section-header">TRADE DECISION</div>', unsafe_allow_html=True)

        risk = latest["risk_score"]
        risk_100 = round(risk * 100)

        if not latest["approved"]:
            reasons_text = ", ".join(latest.get("reasons", ["Risk threshold exceeded"]))
            capital_at_risk = latest["price"] * 0.1
            st.markdown(f"""
            <div class="decision-blocked">
                <div style="font-size:48px; margin-bottom:8px;">🚨</div>
                <div class="decision-text" style="color:#ef4444;">TRADE BLOCKED</div>
                <div class="decision-reason">Reason: {reasons_text}</div>
                <div class="capital-saved">
                    AEGIS protected ${capital_at_risk:,.2f} in capital from a dangerous {latest['signal']} trade
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif latest.get("executed") and latest["signal"] != "HOLD":
            st.markdown(f"""
            <div class="decision-executed">
                <div style="font-size:48px; margin-bottom:8px;">✅</div>
                <div class="decision-text" style="color:#10b981;">TRADE EXECUTED</div>
                <div style="color:#6ee7b7; margin-top:8px; font-size:15px;">
                    {latest['signal']} via {latest['strategy']} @ ${latest['price']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="decision-hold">
                <div style="font-size:48px; margin-bottom:8px;">⏸️</div>
                <div class="decision-text" style="color:#64748b;">HOLDING</div>
                <div style="color:#94a3b8; margin-top:8px; font-size:15px;">
                    No action — market conditions stable
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Risk Gauge ──
    with col_gauge:
        st.markdown('<div class="section-header">RISK FIREWALL</div>', unsafe_allow_html=True)

        bar_color = "#ef4444" if risk > threshold else ("#f59e0b" if risk > 0.4 else "#10b981")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_100,
            number={"suffix": "", "font": {"size": 56, "color": bar_color, "family": "JetBrains Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "#1e293b",
                         "tickfont": {"color": "#475569", "size": 11}},
                "bar": {"color": bar_color, "thickness": 0.8},
                "bgcolor": "#1e293b",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35], "color": "rgba(16,185,129,0.08)"},
                    {"range": [35, 65], "color": "rgba(245,158,11,0.08)"},
                    {"range": [65, 100], "color": "rgba(239,68,68,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.8,
                    "value": threshold * 100,
                },
            },
        ))
        fig_gauge.update_layout(
            plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19",
            height=260, margin=dict(t=30, b=0, l=30, r=30),
            annotations=[dict(
                text=f"Threshold: {threshold*100:.0f}",
                x=0.5, y=-0.05, showarrow=False,
                font=dict(size=12, color="#ef4444", family="JetBrains Mono"),
            )]
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Strategy Panel ──
    with col_strategy:
        st.markdown('<div class="section-header">ACTIVE STRATEGY</div>', unsafe_allow_html=True)

        signal_color = "#10b981" if latest["signal"] == "BUY" else "#ef4444" if latest["signal"] == "SELL" else "#64748b"
        conf_pct = round(latest["confidence"] * 100)

        st.markdown(f"""
        <div class="metric-card" style="padding:20px;">
            <div class="metric-label">Strategy</div>
            <div style="font-size:24px; font-weight:800; color:#f8fafc; margin:8px 0;">
                {latest['strategy']}
            </div>
            <div style="height:1px; background:#1e293b; margin:12px 0;"></div>
            <div class="metric-label">Signal</div>
            <div style="font-size:28px; font-weight:900; color:{signal_color}; margin:4px 0;">
                {latest['signal']}
            </div>
            <div style="height:1px; background:#1e293b; margin:12px 0;"></div>
            <div class="metric-label">Confidence</div>
            <div style="font-size:22px; font-weight:700; color:#3b82f6; margin:4px 0;">
                {conf_pct}%
            </div>
            <div style="background:#1e293b; border-radius:4px; height:6px; margin-top:8px; overflow:hidden;">
                <div style="background:#3b82f6; height:100%; width:{conf_pct}%; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHARTS ROW
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    chart_left, chart_right = st.columns(2)

    # ── Price Chart with Trade Markers ──
    with chart_left:
        st.markdown('<div class="section-header">PRICE ACTION & TRADE DECISIONS</div>', unsafe_allow_html=True)

        cycles = [e["cycle"] for e in logs]
        prices = [e["price"] for e in logs]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cycles, y=prices, mode="lines", name="BTC Price",
            line=dict(color="#3b82f6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.05)",
        ))

        # Blocked markers (big red X)
        bl_c = [e["cycle"] for e in logs if not e["approved"]]
        bl_p = [e["price"] for e in logs if not e["approved"]]
        fig.add_trace(go.Scatter(
            x=bl_c, y=bl_p, mode="markers", name="BLOCKED",
            marker=dict(color="#ef4444", size=16, symbol="x", line=dict(width=2, color="#ef4444")),
        ))

        # Executed BUY
        eb_c = [e["cycle"] for e in logs if e["executed"] and e["signal"] == "BUY"]
        eb_p = [e["price"] for e in logs if e["executed"] and e["signal"] == "BUY"]
        fig.add_trace(go.Scatter(
            x=eb_c, y=eb_p, mode="markers", name="BUY",
            marker=dict(color="#10b981", size=11, symbol="triangle-up"),
        ))

        # Executed SELL
        es_c = [e["cycle"] for e in logs if e["executed"] and e["signal"] == "SELL"]
        es_p = [e["price"] for e in logs if e["executed"] and e["signal"] == "SELL"]
        fig.add_trace(go.Scatter(
            x=es_c, y=es_p, mode="markers", name="SELL",
            marker=dict(color="#f59e0b", size=11, symbol="triangle-down"),
        ))

        fig = plotly_dark(fig, 340)
        fig.update_xaxes(title="Cycle", title_font=dict(color="#475569"))
        fig.update_yaxes(title="Price (USDT)", title_font=dict(color="#475569"))
        st.plotly_chart(fig, use_container_width=True)

    # ── Risk Score Timeline ──
    with chart_right:
        st.markdown('<div class="section-header">RISK SCORE TIMELINE</div>', unsafe_allow_html=True)

        risk_scores = [e["risk_score"] * 100 for e in logs]
        colors = ["#ef4444" if r > threshold * 100 else "#f59e0b" if r > 40 else "#10b981" for r in risk_scores]

        fig_risk = go.Figure()
        fig_risk.add_trace(go.Bar(
            x=cycles, y=risk_scores, name="Risk",
            marker_color=colors,
            marker_line=dict(width=0),
        ))
        fig_risk.add_hline(
            y=threshold * 100, line_dash="dot", line_color="#ef4444", line_width=2,
            annotation_text=f"BLOCK THRESHOLD ({threshold*100:.0f})",
            annotation_font=dict(color="#ef4444", size=11),
            annotation_position="top left",
        )
        fig_risk = plotly_dark(fig_risk, 340)
        fig_risk.update_xaxes(title="Cycle", title_font=dict(color="#475569"))
        fig_risk.update_yaxes(title="Risk Score", title_font=dict(color="#475569"), range=[0, 105])
        st.plotly_chart(fig_risk, use_container_width=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PERFORMANCE COMPARISON
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    perf = api("/performance-comparison")
    if perf.get("with_aegis") and len(perf["with_aegis"]) > 2:
        st.markdown('<div class="section-header">PERFORMANCE — WITH AEGIS vs WITHOUT AEGIS</div>', unsafe_allow_html=True)

        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(
            x=perf["cycles"], y=perf["without_aegis"],
            mode="lines", name="Without AEGIS",
            line=dict(color="#ef4444", width=2, dash="dash"),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.03)",
        ))
        fig_perf.add_trace(go.Scatter(
            x=perf["cycles"], y=perf["with_aegis"],
            mode="lines", name="With AEGIS",
            line=dict(color="#10b981", width=3),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.05)",
        ))
        fig_perf = plotly_dark(fig_perf, 300)
        fig_perf.update_xaxes(title="Cycle")
        fig_perf.update_yaxes(title="Portfolio Value ($)")
        fig_perf.update_layout(
            legend=dict(x=0.02, y=0.98, font=dict(size=13)),
        )

        # Calculate savings
        final_with = perf["with_aegis"][-1]
        final_without = perf["without_aegis"][-1]
        savings = final_with - final_without

        sc1, sc2 = st.columns([3, 1])
        with sc1:
            st.plotly_chart(fig_perf, use_container_width=True)
        with sc2:
            st.markdown(f"""
            <div class="metric-card" style="margin-top:20px;">
                <div class="metric-label">Capital Saved by AEGIS</div>
                <div class="metric-value green" style="font-size:28px;">
                    +${max(savings, 0):,.2f}
                </div>
                <div style="height:1px; background:#1e293b; margin:16px 0;"></div>
                <div class="metric-label">With AEGIS</div>
                <div style="font-size:18px; font-weight:700; color:#10b981;">${final_with:,.2f}</div>
                <div class="metric-label" style="margin-top:12px;">Without AEGIS</div>
                <div style="font-size:18px; font-weight:700; color:#ef4444;">${final_without:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIVE DECISION LOG
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<div class="section-header">LIVE DECISION LOG</div>', unsafe_allow_html=True)

    for entry in reversed(logs[-15:]):
        risk_100 = round(entry["risk_score"] * 100)
        if not entry["approved"]:
            icon = "🚫"
            cls = "blocked"
            status_text = f'<span style="color:#ef4444;font-weight:700;">BLOCKED</span>'
            reason = f' — {", ".join(entry.get("reasons", []))}'
        elif entry["executed"]:
            icon = "✅"
            cls = "executed"
            status_text = f'<span style="color:#10b981;font-weight:700;">EXECUTED</span>'
            reason = ""
        else:
            icon = "⏸️"
            cls = ""
            status_text = f'<span style="color:#64748b;font-weight:700;">HOLD</span>'
            reason = ""

        risk_col = "#ef4444" if risk_100 > 65 else "#f59e0b" if risk_100 > 40 else "#10b981"

        st.markdown(f"""
        <div class="log-entry {cls}">
            <span>{icon}</span>
            <span style="color:#475569;">#{entry['cycle']:03d}</span>
            <span style="color:#3b82f6; font-weight:600;">{entry['strategy']}</span>
            <span style="color:{'#10b981' if entry['signal']=='BUY' else '#ef4444' if entry['signal']=='SELL' else '#64748b'}; font-weight:700;">{entry['signal']}</span>
            <span style="color:#64748b;">@</span>
            <span style="color:#f8fafc;">${entry['price']:,.2f}</span>
            <span style="color:#64748b;">|</span>
            <span style="color:{risk_col}; font-weight:700;">Risk: {risk_100}</span>
            <span style="color:#64748b;">|</span>
            {status_text}{reason}
        </div>
        """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:80px; margin-bottom:20px;">🛡️</div>
        <div style="font-size:28px; color:#f8fafc; font-weight:700;">AEGIS Ready</div>
        <div style="color:#64748b; margin-top:12px; font-size:16px;">
            Click <b>RUN DEMO SCENARIO</b> to see AEGIS protect capital in real-time
        </div>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTO-RUN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if auto_run:
    time.sleep(1.5)
    api("/run-cycle", "POST")
    st.rerun()
