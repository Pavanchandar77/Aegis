"""
AEGIS — Institutional Risk Governor Dashboard
Bloomberg-meets-Linear design. Dense, functional, zero fluff.
"""

import streamlit as st
import requests
import time
import plotly.graph_objects as go
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(page_title="AEGIS", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS: institutional dark theme ───────────────────────────────────────────

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* reset */
.stApp { background: #0a0e17; color: #c4cad4; font-family: 'Inter', -apple-system, sans-serif; }
header[data-testid="stHeader"] { background: #0a0e17; }
.block-container { padding: 1rem 2rem 2rem 2rem; max-width: 100%; }
section[data-testid="stSidebar"] { display: none; }

/* nuke streamlit chrome */
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }

/* typography */
h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; color: #e2e8f0 !important; }
p, span, div, td, th { font-family: 'Inter', sans-serif; }

/* ── top bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0; margin-bottom: 12px;
    border-bottom: 1px solid #1a1f2e;
}
.topbar-left { display: flex; align-items: center; gap: 16px; }
.topbar-brand {
    font-size: 15px; font-weight: 700; letter-spacing: 2px; color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
}
.topbar-status {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.5px; color: #6b7280;
    text-transform: uppercase;
}
.topbar-dot {
    width: 7px; height: 7px; border-radius: 50%;
    display: inline-block; flex-shrink: 0;
}
.topbar-dot.green { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.topbar-dot.red { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.topbar-strat {
    font-size: 11px; color: #6b7280; font-weight: 500;
    padding: 3px 10px; background: #111827; border: 1px solid #1e293b;
    border-radius: 4px; font-family: 'JetBrains Mono', monospace;
}

/* ── metric cards ── */
.mcard {
    background: #111827; border: 1px solid #1a1f2e; border-radius: 6px;
    padding: 12px 14px;
}
.mcard-label {
    font-size: 10px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: #4b5563; margin-bottom: 4px;
}
.mcard-val {
    font-size: 18px; font-weight: 600; color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
}
.mcard-val.up { color: #22c55e; }
.mcard-val.down { color: #ef4444; }
.mcard-val.muted { color: #6b7280; }
.mcard-sub {
    font-size: 10px; color: #4b5563; margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── regime tag ── */
.regime-tag {
    display: inline-block; padding: 2px 8px; border-radius: 3px;
    font-size: 10px; font-weight: 700; letter-spacing: 0.5px;
    font-family: 'JetBrains Mono', monospace;
}
.regime-normal { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
.regime-elevated { background: rgba(234,179,8,0.12); color: #eab308; border: 1px solid rgba(234,179,8,0.25); }
.regime-extreme { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }

/* ── section labels ── */
.sec-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #374151; margin: 16px 0 8px 0;
    padding-bottom: 6px; border-bottom: 1px solid #141924;
}

/* ── trade log table ── */
.tlog-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.tlog-table th {
    text-align: left; padding: 6px 8px; color: #4b5563;
    font-size: 10px; font-weight: 600; letter-spacing: 0.5px;
    text-transform: uppercase; border-bottom: 1px solid #1a1f2e;
}
.tlog-table td {
    padding: 7px 8px; border-bottom: 1px solid #0f1420;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #9ca3af;
}
.tlog-table tr:hover td { background: #111827; }
.tlog-table tr.blocked td { background: rgba(239,68,68,0.04); }
.td-green { color: #22c55e; font-weight: 600; }
.td-red { color: #ef4444; font-weight: 600; }
.td-amber { color: #eab308; font-weight: 600; }
.td-muted { color: #4b5563; }
.td-mono { font-family: 'JetBrains Mono', monospace; }

/* ── risk rule rows ── */
.rule-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0; border-bottom: 1px solid #111827;
    font-size: 12px;
}
.rule-name { width: 130px; color: #6b7280; font-weight: 500; flex-shrink: 0; }
.rule-bar-bg {
    flex: 1; height: 6px; background: #1a1f2e; border-radius: 3px; overflow: hidden;
}
.rule-bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.rule-vals {
    width: 140px; text-align: right; color: #4b5563;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; flex-shrink: 0;
}

/* ── blocked summary card ── */
.blocked-card {
    background: #111827; border: 1px solid #1a1f2e; border-radius: 6px;
    padding: 14px;
}
.blocked-big {
    font-size: 28px; font-weight: 700; color: #ef4444;
    font-family: 'JetBrains Mono', monospace;
}
.blocked-label {
    font-size: 10px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: #4b5563; margin-bottom: 2px;
}
.blocked-reason {
    font-size: 11px; color: #6b7280; margin-top: 8px;
    padding: 6px 8px; background: rgba(239,68,68,0.06);
    border-left: 2px solid #ef4444; border-radius: 0 3px 3px 0;
}

/* ── risk score bar (inline) ── */
.risk-inline {
    display: inline-flex; align-items: center; gap: 6px;
}
.risk-bar-sm {
    width: 40px; height: 4px; background: #1a1f2e; border-radius: 2px;
    overflow: hidden; display: inline-block; vertical-align: middle;
}
.risk-bar-sm-fill { height: 100%; border-radius: 2px; }

/* ── buttons: compact ── */
.stButton > button {
    font-size: 11px !important; font-weight: 600 !important;
    padding: 5px 14px !important; border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important; letter-spacing: 0.3px !important;
    border: 1px solid #1e293b !important; background: #111827 !important;
    color: #9ca3af !important; transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #1a1f2e !important; color: #e2e8f0 !important;
    border-color: #374151 !important;
}
.stButton > button[kind="primary"] {
    background: #1e3a5f !important; border-color: #2563eb !important;
    color: #93c5fd !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1e40af !important; color: #dbeafe !important;
}

/* toggle */
[data-testid="stBaseButton-secondary"] {
    font-size: 11px !important;
}

/* plotly overrides */
.js-plotly-plot .plotly .modebar { display: none !important; }
</style>""", unsafe_allow_html=True)


# ─── helpers ─────────────────────────────────────────────────────────────────

def get(endpoint):
    try:
        return requests.get(f"{API}{endpoint}", timeout=5).json()
    except Exception as e:
        return {"error": str(e)}

def post(endpoint):
    try:
        return requests.post(f"{API}{endpoint}", timeout=10).json()
    except Exception as e:
        return {"error": str(e)}

def dark_fig(fig, h=260):
    fig.update_layout(
        plot_bgcolor="#0a0e17", paper_bgcolor="#0a0e17",
        font=dict(family="Inter, sans-serif", color="#4b5563", size=11),
        height=h, margin=dict(t=8, b=32, l=48, r=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6b7280", size=10)),
        xaxis=dict(gridcolor="#111827", zerolinecolor="#111827", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#111827", zerolinecolor="#111827", tickfont=dict(size=10)),
    )
    return fig

def risk_color(score):
    if score > 0.65: return "#ef4444"
    if score > 0.40: return "#eab308"
    return "#22c55e"

def risk_class(score):
    if score > 0.65: return "td-red"
    if score > 0.40: return "td-amber"
    return "td-green"

def regime_class(vol_pct):
    if vol_pct > 2.0: return "regime-extreme", "EXTREME"
    if vol_pct > 0.8: return "regime-elevated", "ELEVATED"
    return "regime-normal", "NORMAL"


# ─── data ────────────────────────────────────────────────────────────────────

status = get("/status")
if "error" in status:
    st.markdown("""<div style="text-align:center;padding:120px 20px;">
        <div style="font-size:14px;color:#ef4444;font-weight:600;letter-spacing:1px;">AEGIS API OFFLINE</div>
        <div style="color:#4b5563;margin-top:8px;font-size:12px;">
            Start the backend: <code style="color:#93c5fd;">python -m aegis.api</code>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

logs = get("/logs?last_n=50").get("logs", [])
latest = logs[-1] if logs else None
threshold = status.get("risk_threshold", 0.65)
price = status.get("current_price") or 0
vol = (status.get("volatility") or 0) * 100
pnl = status.get("pnl", 0)
pnl_pct = status.get("pnl_pct", 0)
pv = status.get("portfolio_value", 100000)
blocked = status.get("trades_blocked", 0)
approved = status.get("trades_approved", 0)
total = blocked + approved
vol_cls, vol_label = regime_class(vol)
is_volatile = status.get("volatile_mode", False)


# ─── top bar ─────────────────────────────────────────────────────────────────

active_strat = latest["strategy"] if latest else "—"
dot_cls = "red" if is_volatile else "green"
status_label = "Volatile" if is_volatile else "Active"

st.markdown(f"""<div class="topbar">
    <div class="topbar-left">
        <span class="topbar-brand">AEGIS</span>
        <span class="topbar-status"><span class="topbar-dot {dot_cls}"></span> {status_label}</span>
        <span class="topbar-strat">{active_strat}</span>
        <span class="regime-tag {vol_cls}">{vol_label}</span>
    </div>
</div>""", unsafe_allow_html=True)

# controls — compact, right-aligned feel via narrow columns
_sp, bc1, bc2, bc3, bc4, bc5 = st.columns([4, 1.2, 1.2, 1.2, 1, 0.8])
with bc1:
    demo_go = st.button("Run Demo", type="primary", use_container_width=True)
with bc2:
    cycle_go = st.button("Single Cycle", use_container_width=True)
with bc3:
    vol_go = st.button("Vol Spike" if not is_volatile else "Vol Off", use_container_width=True)
with bc4:
    reset_go = st.button("Reset", use_container_width=True)
with bc5:
    auto = st.toggle("Auto", value=False)

if demo_go:
    post("/demo-scenario")
    st.rerun()
if cycle_go:
    post("/run-cycle")
    st.rerun()
if vol_go:
    post(f"/set-volatile?volatile={'false' if is_volatile else 'true'}")
    st.rerun()
if reset_go:
    post("/reset")
    st.rerun()


# ─── row 1: metrics ─────────────────────────────────────────────────────────

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">BTC / USDT</div>
        <div class="mcard-val">${price:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">Volatility</div>
        <div class="mcard-val">{vol:.2f}%</div>
        <div class="mcard-sub"><span class="regime-tag {vol_cls}">{vol_label}</span></div>
    </div>""", unsafe_allow_html=True)
with k3:
    pnl_cls = "up" if pnl >= 0 else "down"
    sign = "+" if pnl >= 0 else ""
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">P&L</div>
        <div class="mcard-val {pnl_cls}">{sign}${pnl:,.2f}</div>
        <div class="mcard-sub">{sign}{pnl_pct:.2f}%</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">Portfolio</div>
        <div class="mcard-val">${pv:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with k5:
    ratio_str = f"{approved}/{total}" if total else "0/0"
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">Approved / Total</div>
        <div class="mcard-val">{ratio_str}</div>
    </div>""", unsafe_allow_html=True)
with k6:
    st.markdown(f"""<div class="mcard">
        <div class="mcard-label">Blocked</div>
        <div class="mcard-val down">{blocked}</div>
    </div>""", unsafe_allow_html=True)


# ─── row 2: trade log + risk breakdown ───────────────────────────────────────

if logs:
    st.markdown('<div class="sec-label">Trade Decision Log</div>', unsafe_allow_html=True)

    col_log, col_risk = st.columns([3, 2])

    with col_log:
        recent = list(reversed(logs[-12:]))
        rows_html = ""
        for e in recent:
            ts = e.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                t_str = dt.strftime("%H:%M:%S")
            except Exception:
                t_str = "—"

            sig = e["signal"]
            sig_cls = "td-green" if sig == "BUY" else "td-red" if sig == "SELL" else "td-muted"

            rs = e["risk_score"]
            rs_100 = round(rs * 100)
            r_cls = risk_class(rs)
            r_col = risk_color(rs)

            size = f"${e['price'] * 0.1:,.0f}"

            if not e["approved"]:
                dec_html = '<span class="td-red">BLOCKED</span>'
                row_cls = "blocked"
            elif e["executed"]:
                dec_html = '<span class="td-green">Approved</span>'
                row_cls = ""
            else:
                dec_html = '<span class="td-muted">Hold</span>'
                row_cls = ""

            rows_html += f"""<tr class="{row_cls}">
                <td>{t_str}</td>
                <td>BTC/USDT</td>
                <td class="{sig_cls}">{sig}</td>
                <td><span class="{r_cls}">{rs_100}</span>
                    <span class="risk-bar-sm"><span class="risk-bar-sm-fill" style="width:{rs_100}%;background:{r_col};"></span></span>
                </td>
                <td>{size}</td>
                <td>{dec_html}</td>
            </tr>"""

        st.markdown(f"""<table class="tlog-table">
            <thead><tr>
                <th>Time</th><th>Ticker</th><th>Signal</th><th>Risk</th><th>Size</th><th>Decision</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

    with col_risk:
        st.markdown('<div class="sec-label">Risk Rules — Live State</div>', unsafe_allow_html=True)

        rb = get("/risk-breakdown")
        rules = rb.get("rules", []) if "error" not in rb else []

        for rule in rules:
            pct = min(rule["pct"], 1.0)
            pct_w = round(pct * 100)
            col = risk_color(pct)
            status_tag = rule["status"]
            s_cls = "regime-extreme" if status_tag in ("Extreme", "Triggered") else \
                    "regime-elevated" if status_tag in ("Elevated", "Warning", "Active") else "regime-normal"

            st.markdown(f"""<div class="rule-row">
                <span class="rule-name">{rule['name']}</span>
                <div class="rule-bar-bg"><div class="rule-bar-fill" style="width:{pct_w}%;background:{col};"></div></div>
                <span class="rule-vals">{rule['current']} / {rule['limit']}
                    <span class="regime-tag {s_cls}" style="margin-left:6px;font-size:9px;">{status_tag}</span>
                </span>
            </div>""", unsafe_allow_html=True)

        # composite weights
        weights = rb.get("composite_weights", {})
        if weights:
            w_html = " ".join(
                f'<span style="color:#4b5563;font-size:10px;font-family:JetBrains Mono,monospace;'
                f'padding:2px 6px;background:#111827;border-radius:3px;margin:2px;">'
                f'{k} {int(v*100)}%</span>'
                for k, v in weights.items()
            )
            st.markdown(f'<div style="margin-top:12px;">'
                        f'<span style="font-size:10px;color:#374151;font-weight:600;letter-spacing:0.5px;">WEIGHTS </span>'
                        f'{w_html}</div>', unsafe_allow_html=True)


    # ─── row 3: charts + blocked summary ─────────────────────────────────────

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    ch1, ch2, ch3 = st.columns([2, 2, 1])

    # equity curve
    with ch1:
        st.markdown('<div class="sec-label">Equity Curve</div>', unsafe_allow_html=True)

        perf = get("/performance-comparison")
        if perf.get("with_aegis") and len(perf["with_aegis"]) > 2:
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(
                x=perf["cycles"], y=perf["without_aegis"],
                mode="lines", name="No Protection",
                line=dict(color="#ef4444", width=1.5, dash="dot"),
            ))
            fig_eq.add_trace(go.Scatter(
                x=perf["cycles"], y=perf["with_aegis"],
                mode="lines", name="With AEGIS",
                line=dict(color="#22c55e", width=2),
            ))
            fig_eq = dark_fig(fig_eq, 220)
            fig_eq.update_xaxes(title_text="Cycle", title_font=dict(size=10, color="#374151"))
            fig_eq.update_yaxes(title_text="Value ($)", title_font=dict(size=10, color="#374151"))
            st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})

    # price + risk overlay
    with ch2:
        st.markdown('<div class="sec-label">Price & Risk Score</div>', unsafe_allow_html=True)

        cycles = [e["cycle"] for e in logs]
        prices = [e["price"] for e in logs]
        risks = [e["risk_score"] * 100 for e in logs]

        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(
            x=cycles, y=prices, mode="lines", name="Price",
            line=dict(color="#3b82f6", width=1.5), yaxis="y",
        ))

        # blocked markers
        bl_c = [e["cycle"] for e in logs if not e["approved"]]
        bl_p = [e["price"] for e in logs if not e["approved"]]
        if bl_c:
            fig_pr.add_trace(go.Scatter(
                x=bl_c, y=bl_p, mode="markers", name="Blocked",
                marker=dict(color="#ef4444", size=8, symbol="x", line=dict(width=1.5, color="#ef4444")),
                yaxis="y",
            ))

        # risk on secondary axis
        fig_pr.add_trace(go.Scatter(
            x=cycles, y=risks, mode="lines", name="Risk",
            line=dict(color="#eab308", width=1, dash="dot"), yaxis="y2",
        ))

        fig_pr = dark_fig(fig_pr, 220)
        fig_pr.update_layout(
            yaxis2=dict(
                overlaying="y", side="right", range=[0, 105],
                gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#4b5563", size=9),
                title_text="Risk", title_font=dict(size=10, color="#374151"),
            ),
            yaxis=dict(title_text="Price", title_font=dict(size=10, color="#374151")),
            xaxis=dict(title_text="Cycle", title_font=dict(size=10, color="#374151")),
        )
        st.plotly_chart(fig_pr, use_container_width=True, config={"displayModeBar": False})

    # blocked summary
    with ch3:
        st.markdown('<div class="sec-label">Block Summary</div>', unsafe_allow_html=True)

        blocked_entries = [e for e in logs if not e["approved"]]
        capital_saved = sum(e["price"] * 0.1 for e in blocked_entries)
        last_reason = ", ".join(blocked_entries[-1]["reasons"]) if blocked_entries else "—"

        st.markdown(f"""<div class="blocked-card">
            <div class="blocked-label">Capital Protected</div>
            <div class="blocked-big">${capital_saved:,.0f}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="blocked-card" style="margin-top:8px;">
            <div class="blocked-label">Blocks This Session</div>
            <div style="font-size:22px;font-weight:700;color:#ef4444;font-family:'JetBrains Mono',monospace;">{len(blocked_entries)}</div>
        </div>""", unsafe_allow_html=True)

        if blocked_entries:
            st.markdown(f"""<div class="blocked-card" style="margin-top:8px;">
                <div class="blocked-label">Last Block Reason</div>
                <div class="blocked-reason">{last_reason}</div>
            </div>""", unsafe_allow_html=True)

else:
    st.markdown("""<div style="text-align:center;padding:80px 20px;">
        <div style="font-size:13px;color:#4b5563;font-weight:600;letter-spacing:1px;">NO TRADES YET</div>
        <div style="color:#374151;margin-top:6px;font-size:12px;">
            Click <strong>Run Demo</strong> to start the trading simulation.
        </div>
    </div>""", unsafe_allow_html=True)


# ─── auto-run loop ───────────────────────────────────────────────────────────

if auto:
    time.sleep(2.5)
    post("/run-cycle")
    st.rerun()
