"""
AEGIS Risk Governor Dashboard
Self-contained Streamlit demo — 4 states, dark theme, institutional feel.
Run: streamlit run aegis/dashboard.py
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="AEGIS", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp { background: #0a0e17; color: #c4cad4; font-family: 'Inter', sans-serif; }
header[data-testid="stHeader"] { background: #0a0e17; border-bottom: 1px solid #151a26; }
.block-container { padding: 0.8rem 2rem 2rem 2rem; max-width: 100%; }

/* Hide streamlit defaults */
#MainMenu, footer, [data-testid="stToolbar"] { display: none; }
div[data-testid="stDecoration"] { display: none; }

/* Metric cards */
.metric-card {
    background: #111827; border: 1px solid #1e293b; border-radius: 6px;
    padding: 12px 16px; text-align: left;
}
.metric-label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.metric-value { font-size: 18px; font-weight: 600; color: #e2e8f0; }
.metric-value.positive { color: #22c55e; }
.metric-value.negative { color: #ef4444; }
.metric-value.green { color: #22c55e; }
.metric-value.red { color: #ef4444; }

/* Top bar */
.top-bar {
    display: flex; align-items: center; gap: 16px;
    padding: 8px 0 12px 0; border-bottom: 1px solid #1e293b; margin-bottom: 16px;
}
.aegis-brand { font-size: 15px; font-weight: 600; color: #00D4FF; letter-spacing: 1px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.status-green { background: #22c55e; box-shadow: 0 0 6px #22c55e80; }
.status-red { background: #ef4444; box-shadow: 0 0 6px #ef444480; }
.tag { font-size: 11px; padding: 2px 8px; border-radius: 3px; font-weight: 500; }
.tag-normal { background: #064e3b; color: #6ee7b7; }
.tag-extreme { background: #7f1d1d; color: #fca5a5; }
.strategy-label { font-size: 12px; color: #6b7280; }

/* Trade log table */
.trade-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.trade-table th {
    text-align: left; padding: 8px 10px; color: #6b7280; font-weight: 500;
    border-bottom: 1px solid #1e293b; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.5px;
}
.trade-table td { padding: 7px 10px; border-bottom: 1px solid #141926; color: #c4cad4; }
.trade-table tr:hover { background: #111827; }
.approved { color: #22c55e; font-weight: 500; }
.blocked { color: #ef4444; font-weight: 500; }
.risk-low { color: #22c55e; }
.risk-med { color: #eab308; }
.risk-high { color: #ef4444; }
.size-blocked { color: #6b7280; text-decoration: line-through; }
.reason-text { color: #9ca3af; font-size: 11px; font-style: italic; }

/* Risk rule bars */
.rule-container { margin-bottom: 14px; }
.rule-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.rule-name { font-size: 12px; color: #9ca3af; }
.rule-value { font-size: 12px; color: #e2e8f0; }
.rule-bar-bg { background: #1e293b; border-radius: 3px; height: 6px; width: 100%; }
.rule-bar { border-radius: 3px; height: 6px; transition: width 0.3s ease; }
.bar-green { background: #22c55e; }
.bar-yellow { background: #eab308; }
.bar-red { background: #ef4444; }

/* Section headers */
.section-header { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; font-weight: 500; }

/* Summary card */
.summary-card { background: #111827; border: 1px solid #1e293b; border-radius: 6px; padding: 16px; }
.summary-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #141926; }
.summary-row:last-child { border-bottom: none; }
.summary-label { font-size: 12px; color: #6b7280; }
.summary-value { font-size: 13px; color: #e2e8f0; font-weight: 500; }
.summary-value.highlight { color: #22c55e; font-size: 18px; }

/* Button styling */
div.stButton > button {
    background: #1e293b; color: #c4cad4; border: 1px solid #334155;
    font-size: 12px; padding: 4px 14px; border-radius: 4px; font-weight: 500;
    height: 32px; min-height: 32px;
}
div.stButton > button:hover { background: #334155; border-color: #475569; color: #e2e8f0; }
</style>""", unsafe_allow_html=True)


# ─── Session State Init ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "state": "IDLE",
        "btc_price": 67725.57,
        "volatility": 0.32,
        "vol_regime": "NORMAL",
        "portfolio_value": 100000.00,
        "pnl": 0.00,
        "approved_count": 0,
        "blocked_count": 0,
        "trades": [],
        "equity_curve": [100000.00],
        "capital_saved": 0.0,
        "last_block_reason": "—",
        "sector_concentration": 18.0,
        "max_position_pct": 24.0,
        "portfolio_drawdown": 1.2,
        "demo_done": False,
        "spike_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Trade Data ──────────────────────────────────────────────────────────────

DEMO_TRADES = [
    {"time": "10:41:01", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 12, "size": 8200,  "decision": "APPROVED", "reason": "", "pnl_delta": 42},
    {"time": "10:41:04", "ticker": "BTC/USDT", "dir": "SELL", "risk": 23, "size": 5400,  "decision": "APPROVED", "reason": "", "pnl_delta": 28},
    {"time": "10:41:07", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 18, "size": 12100, "decision": "APPROVED", "reason": "", "pnl_delta": 55},
    {"time": "10:41:10", "ticker": "BTC/USDT", "dir": "SELL", "risk": 31, "size": 6800,  "decision": "APPROVED", "reason": "", "pnl_delta": -15},
    {"time": "10:41:13", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 9,  "size": 4900,  "decision": "APPROVED", "reason": "", "pnl_delta": 22},
    {"time": "10:41:16", "ticker": "BTC/USDT", "dir": "SELL", "risk": 27, "size": 11300, "decision": "APPROVED", "reason": "", "pnl_delta": 68},
    {"time": "10:41:19", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 14, "size": 7600,  "decision": "APPROVED", "reason": "", "pnl_delta": -20},
    {"time": "10:41:22", "ticker": "BTC/USDT", "dir": "SELL", "risk": 22, "size": 9100,  "decision": "APPROVED", "reason": "", "pnl_delta": 35},
]

SPIKE_TRADES = [
    {"time": "10:41:31", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 58, "size": 13500, "decision": "APPROVED", "reason": "", "pnl_delta": -45},
    {"time": "10:41:34", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 72, "size": 14200, "decision": "BLOCKED",  "reason": "Volatility regime exceeded", "pnl_delta": 0},
    {"time": "10:41:37", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 85, "size": 14700, "decision": "BLOCKED",  "reason": "Concentration limit: 24.8% / 25%", "pnl_delta": 0},
    {"time": "10:41:40", "ticker": "BTC/USDT", "dir": "BUY",  "risk": 91, "size": 13600, "decision": "BLOCKED",  "reason": "Max drawdown proximity", "pnl_delta": 0},
]

# ─── Helper: Risk bar color ─────────────────────────────────────────────────
def bar_color(pct):
    if pct < 60:
        return "bar-green"
    elif pct < 85:
        return "bar-yellow"
    return "bar-red"

def risk_class(score):
    if score <= 30:
        return "risk-low"
    elif score <= 60:
        return "risk-med"
    return "risk-high"


# ─── Top Bar ─────────────────────────────────────────────────────────────────
s = st.session_state

top_cols = st.columns([2, 0.5, 1.5, 1, 1, 1, 1])

with top_cols[0]:
    regime_tag = f'<span class="tag tag-normal">NORMAL</span>' if s.vol_regime == "NORMAL" else f'<span class="tag tag-extreme">EXTREME</span>'
    dot_class = "status-green"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding-top:6px;">
        <span class="aegis-brand">AEGIS</span>
        <span class="status-dot {dot_class}"></span>
        <span class="strategy-label">MeanReversion</span>
        {regime_tag}
    </div>
    """, unsafe_allow_html=True)

with top_cols[4]:
    demo_btn = st.button("Run Demo", disabled=s.demo_done, use_container_width=True)
with top_cols[5]:
    spike_btn = st.button("Volatility Spike", disabled=(not s.demo_done or s.spike_done), use_container_width=True)
with top_cols[6]:
    reset_btn = st.button("Reset", use_container_width=True)


# ─── Metric Cards ────────────────────────────────────────────────────────────
st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
mc = st.columns(6)

def render_metric(col, label, value, css_class=""):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {css_class}">{value}</div>
        </div>
        """, unsafe_allow_html=True)

pnl_class = "positive" if s.pnl >= 0 else "negative"
pnl_prefix = "+" if s.pnl >= 0 else ""

render_metric(mc[0], "BTC Price", f"${s.btc_price:,.2f}")
render_metric(mc[1], "Volatility", f"{s.volatility:.2f}%")
render_metric(mc[2], "Portfolio Value", f"${s.portfolio_value:,.2f}")
render_metric(mc[3], "P&L", f"{pnl_prefix}${s.pnl:,.2f}", pnl_class)
render_metric(mc[4], "Trades Approved", str(s.approved_count), "green")
render_metric(mc[5], "Trades Blocked", str(s.blocked_count), "red" if s.blocked_count > 0 else "")


# ─── Row 2: Trade Log + Risk Rules ──────────────────────────────────────────
st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
r2_left, r2_right = st.columns([65, 35])

with r2_left:
    st.markdown('<div class="section-header">Trade Decision Log</div>', unsafe_allow_html=True)
    log_placeholder = st.empty()

with r2_right:
    st.markdown('<div class="section-header">Risk Rules</div>', unsafe_allow_html=True)
    risk_placeholder = st.empty()


# ─── Row 3: Equity Curve + Blocked Summary ──────────────────────────────────
st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
r3_left, r3_right = st.columns(2)

with r3_left:
    st.markdown('<div class="section-header">P&L Equity Curve</div>', unsafe_allow_html=True)
    chart_placeholder = st.empty()

with r3_right:
    st.markdown('<div class="section-header">Blocked Trades Summary</div>', unsafe_allow_html=True)
    summary_placeholder = st.empty()


# ─── Render Functions ────────────────────────────────────────────────────────

def render_trade_log():
    if not s.trades:
        log_placeholder.markdown("""
        <div style="color:#4b5563;font-size:13px;padding:40px 0;text-align:center;">
            No trades yet. Click "Run Demo" to begin.
        </div>
        """, unsafe_allow_html=True)
        return

    rows_html = ""
    for t in s.trades:
        rc = risk_class(t["risk"])
        if t["decision"] == "APPROVED":
            dec_html = '<span class="approved">APPROVED</span>'
            size_html = f'${t["size"]:,}'
        else:
            dec_html = '<span class="blocked">BLOCKED</span>'
            size_html = f'<span class="size-blocked">${t["size"]:,}</span>'
        reason_html = f'<span class="reason-text">{t["reason"]}</span>' if t["reason"] else ""
        rows_html += f"""
        <tr>
            <td>{t["time"]}</td>
            <td>{t["ticker"]}</td>
            <td>{t["dir"]}</td>
            <td><span class="{rc}">{t["risk"]}</span></td>
            <td>{size_html}</td>
            <td>{dec_html}</td>
            <td>{reason_html}</td>
        </tr>"""

    log_placeholder.markdown(f"""
    <table class="trade-table">
        <thead><tr>
            <th>Time</th><th>Ticker</th><th>Direction</th><th>Risk</th>
            <th>Size</th><th>Decision</th><th>Reason</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)


def render_risk_rules():
    conc_pct = (s.sector_concentration / 25) * 100
    pos_pct = (s.max_position_pct / 100) * 100
    dd_pct = (s.portfolio_drawdown / 5) * 100

    regime_color = "#22c55e" if s.vol_regime == "NORMAL" else "#ef4444"
    regime_text = s.vol_regime

    risk_placeholder.markdown(f"""
    <div style="background:#111827;border:1px solid #1e293b;border-radius:6px;padding:16px;">
        <div class="rule-container">
            <div class="rule-header">
                <span class="rule-name">Sector Concentration</span>
                <span class="rule-value">{s.sector_concentration:.1f}% / 25%</span>
            </div>
            <div class="rule-bar-bg"><div class="rule-bar {bar_color(conc_pct)}" style="width:{min(conc_pct,100):.1f}%"></div></div>
        </div>
        <div class="rule-container">
            <div class="rule-header">
                <span class="rule-name">Max Position Size</span>
                <span class="rule-value">${s.max_position_pct:.0f}K / $50K</span>
            </div>
            <div class="rule-bar-bg"><div class="rule-bar {bar_color(pos_pct)}" style="width:{min(pos_pct,100):.1f}%"></div></div>
        </div>
        <div class="rule-container">
            <div class="rule-header">
                <span class="rule-name">Portfolio Drawdown</span>
                <span class="rule-value">{s.portfolio_drawdown:.1f}% / 5%</span>
            </div>
            <div class="rule-bar-bg"><div class="rule-bar {bar_color(dd_pct)}" style="width:{min(dd_pct,100):.1f}%"></div></div>
        </div>
        <div class="rule-container" style="margin-bottom:0;">
            <div class="rule-header">
                <span class="rule-name">Volatility Regime</span>
                <span style="color:{regime_color};font-size:13px;font-weight:600;">{regime_text}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_equity_curve():
    df = pd.DataFrame({"Portfolio": s.equity_curve})
    chart_placeholder.line_chart(df, color="#00D4FF", height=180, use_container_width=True)


def render_summary():
    saved_display = f"${s.capital_saved:,.0f}" if s.capital_saved > 0 else "$0"
    summary_placeholder.markdown(f"""
    <div class="summary-card">
        <div class="summary-row">
            <span class="summary-label">Capital Saved</span>
            <span class="summary-value highlight">{saved_display}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Trades Blocked Today</span>
            <span class="summary-value">{s.blocked_count}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Last Block Reason</span>
            <span class="summary-value">{s.last_block_reason}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_all():
    render_trade_log()
    render_risk_rules()
    render_equity_curve()
    render_summary()


# ─── State Machine ───────────────────────────────────────────────────────────

# Concentration steps during demo (8 trades: 18 -> ~22)
DEMO_CONC_STEPS = [18.5, 19.0, 19.5, 19.8, 20.2, 20.8, 21.3, 21.8]
DEMO_POS_STEPS  = [24.0, 24.5, 25.5, 26.0, 26.5, 27.0, 28.0, 29.0]
DEMO_DD_STEPS   = [1.2, 1.3, 1.3, 1.5, 1.4, 1.4, 1.5, 1.5]

SPIKE_CONC_STEPS = [22.5, 23.5, 24.8, 24.8]
SPIKE_POS_STEPS  = [31.0, 31.0, 31.0, 31.0]
SPIKE_DD_STEPS   = [2.1, 3.2, 4.1, 4.1]


if reset_btn:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

elif demo_btn and not s.demo_done:
    # Render initial state first
    render_all()

    for i, trade in enumerate(DEMO_TRADES):
        time.sleep(2.5)
        s.trades.append(trade)
        s.approved_count += 1
        s.pnl += trade["pnl_delta"]
        s.portfolio_value = 100000.00 + s.pnl
        s.equity_curve.append(s.portfolio_value)
        s.sector_concentration = DEMO_CONC_STEPS[i]
        s.max_position_pct = DEMO_POS_STEPS[i]
        s.portfolio_drawdown = DEMO_DD_STEPS[i]
        # Slight BTC price drift
        s.btc_price += [12.30, -8.50, 22.10, -5.40, 15.70, -3.20, 18.90, -10.60][i]

        # Re-render all components
        render_all()

        # Update metrics inline (re-render top section via rewriting)
        mc[0].markdown(f'<div class="metric-card"><div class="metric-label">BTC Price</div><div class="metric-value">${s.btc_price:,.2f}</div></div>', unsafe_allow_html=True)
        mc[1].markdown(f'<div class="metric-card"><div class="metric-label">Volatility</div><div class="metric-value">{s.volatility:.2f}%</div></div>', unsafe_allow_html=True)
        mc[2].markdown(f'<div class="metric-card"><div class="metric-label">Portfolio Value</div><div class="metric-value">${s.portfolio_value:,.2f}</div></div>', unsafe_allow_html=True)
        pnl_c = "positive" if s.pnl >= 0 else "negative"
        pnl_p = "+" if s.pnl >= 0 else ""
        mc[3].markdown(f'<div class="metric-card"><div class="metric-label">P&L</div><div class="metric-value {pnl_c}">{pnl_p}${s.pnl:,.2f}</div></div>', unsafe_allow_html=True)
        mc[4].markdown(f'<div class="metric-card"><div class="metric-label">Trades Approved</div><div class="metric-value green">{s.approved_count}</div></div>', unsafe_allow_html=True)
        mc[5].markdown(f'<div class="metric-card"><div class="metric-label">Trades Blocked</div><div class="metric-value">{s.blocked_count}</div></div>', unsafe_allow_html=True)

    s.demo_done = True
    s.state = "DEMO_DONE"
    st.rerun()

elif spike_btn and s.demo_done and not s.spike_done:
    render_all()

    # First: volatility jumps
    time.sleep(1)
    s.volatility = 4.80
    s.vol_regime = "EXTREME"
    # Force top bar to show EXTREME (will show on next rerun, but we update metrics now)
    mc[1].markdown(f'<div class="metric-card"><div class="metric-label">Volatility</div><div class="metric-value red">4.80%</div></div>', unsafe_allow_html=True)

    running_saved = 0.0
    for i, trade in enumerate(SPIKE_TRADES):
        time.sleep(2.5)
        s.trades.append(trade)
        s.sector_concentration = SPIKE_CONC_STEPS[i]
        s.max_position_pct = SPIKE_POS_STEPS[i]
        s.portfolio_drawdown = SPIKE_DD_STEPS[i]

        if trade["decision"] == "APPROVED":
            s.approved_count += 1
            s.pnl += trade["pnl_delta"]
        else:
            s.blocked_count += 1
            running_saved += trade["size"]
            s.capital_saved = running_saved
            s.last_block_reason = trade["reason"]

        s.portfolio_value = 100000.00 + s.pnl
        s.equity_curve.append(s.portfolio_value)
        s.btc_price += [-180.40, -420.20, -310.50, -250.80][i]

        render_all()

        # Update metrics
        mc[0].markdown(f'<div class="metric-card"><div class="metric-label">BTC Price</div><div class="metric-value">${s.btc_price:,.2f}</div></div>', unsafe_allow_html=True)
        mc[1].markdown(f'<div class="metric-card"><div class="metric-label">Volatility</div><div class="metric-value red">4.80%</div></div>', unsafe_allow_html=True)
        mc[2].markdown(f'<div class="metric-card"><div class="metric-label">Portfolio Value</div><div class="metric-value">${s.portfolio_value:,.2f}</div></div>', unsafe_allow_html=True)
        pnl_c = "positive" if s.pnl >= 0 else "negative"
        pnl_p = "+" if s.pnl >= 0 else ""
        mc[3].markdown(f'<div class="metric-card"><div class="metric-label">P&L</div><div class="metric-value {pnl_c}">{pnl_p}${s.pnl:,.2f}</div></div>', unsafe_allow_html=True)
        mc[4].markdown(f'<div class="metric-card"><div class="metric-label">Trades Approved</div><div class="metric-value green">{s.approved_count}</div></div>', unsafe_allow_html=True)
        blocked_c = "red" if s.blocked_count > 0 else ""
        mc[5].markdown(f'<div class="metric-card"><div class="metric-label">Trades Blocked</div><div class="metric-value {blocked_c}">{s.blocked_count}</div></div>', unsafe_allow_html=True)

    s.spike_done = True
    s.state = "FINAL"
    st.rerun()

else:
    # Static render for IDLE / DEMO_DONE / FINAL states
    render_all()
