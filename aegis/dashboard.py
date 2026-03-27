"""
AEGIS Streamlit Dashboard

Shows real-time:
  - Current BTC price
  - Active strategy & signal
  - Risk score gauge
  - Trade decisions (EXECUTED vs BLOCKED)
  - Price chart with trade markers
  - Session statistics
"""

import streamlit as st
import requests
import time
import plotly.graph_objects as go
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AEGIS Risk Governor", page_icon="🛡️", layout="wide")


def fetch(endpoint: str, method: str = "GET", params: dict | None = None):
    try:
        if method == "POST":
            r = requests.post(f"{API_URL}{endpoint}", params=params, timeout=5)
        else:
            r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ── Header ──
st.title("🛡️ AEGIS — Autonomous Risk Governor")
st.caption("Real-time AI trading risk management system")

# ── Controls ──
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)

with col_ctrl1:
    if st.button("▶️ Run Cycle", use_container_width=True, type="primary"):
        result = fetch("/run-cycle", method="POST")
        if "error" not in result:
            st.session_state["last_result"] = result

with col_ctrl2:
    if st.button("⚡ Volatile ON", use_container_width=True):
        fetch("/set-volatile?volatile=true", method="POST")
        st.toast("⚠️ Volatile mode ACTIVATED!", icon="⚡")

with col_ctrl3:
    if st.button("😌 Volatile OFF", use_container_width=True):
        fetch("/set-volatile?volatile=false", method="POST")
        st.toast("Market calmed down", icon="✅")

with col_ctrl4:
    auto_run = st.toggle("Auto-run", value=False)

# ── Status ──
status = fetch("/status")

if "error" in status:
    st.error(f"Cannot connect to AEGIS API at {API_URL}. Start the API first: `python -m aegis.api`")
    st.stop()

# ── Key Metrics ──
st.divider()
c1, c2, c3, c4, c5 = st.columns(5)

price = status.get("current_price", 0)
c1.metric("BTC/USDT", f"${price:,.2f}" if price else "N/A")
c2.metric("Portfolio", f"${status.get('portfolio_value', 0):,.2f}")
c3.metric("Trades Blocked", status.get("trades_blocked", 0))
c4.metric("Trades Approved", status.get("trades_approved", 0))
stats = status.get("stats", {})
c5.metric("Block Rate", f"{stats.get('block_rate', 0):.1%}")

# ── Latest Decision ──
st.divider()
logs_data = fetch("/logs?last_n=30")
logs = logs_data.get("logs", [])

if logs:
    latest = logs[-1]

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Latest Decision")

        # Big status indicator
        if not latest["approved"]:
            st.markdown(
                """<div style="background-color:#ff4444; color:white; padding:20px;
                border-radius:10px; text-align:center; font-size:24px; font-weight:bold;">
                ❌ TRADE BLOCKED</div>""",
                unsafe_allow_html=True,
            )
            st.error(f"**Reason:** {', '.join(latest.get('reasons', ['Risk too high']))}")
        elif latest.get("executed"):
            st.markdown(
                """<div style="background-color:#00cc66; color:white; padding:20px;
                border-radius:10px; text-align:center; font-size:24px; font-weight:bold;">
                ✅ TRADE EXECUTED</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """<div style="background-color:#888888; color:white; padding:20px;
                border-radius:10px; text-align:center; font-size:24px; font-weight:bold;">
                ⏸ HOLD</div>""",
                unsafe_allow_html=True,
            )

        st.markdown(f"""
        | Field | Value |
        |-------|-------|
        | **Strategy** | {latest['strategy']} |
        | **Signal** | {latest['signal']} |
        | **Confidence** | {latest['confidence']:.3f} |
        | **Risk Score** | {latest['risk_score']:.4f} |
        | **Price** | ${latest['price']:,.2f} |
        | **P&L** | ${latest.get('pnl', 0):,.2f} |
        """)

    with col_right:
        st.subheader("Risk Score Gauge")

        risk = latest["risk_score"]
        threshold = status.get("risk_threshold", 0.65)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk,
            number={"font": {"size": 48}},
            delta={"reference": threshold, "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
            gauge={
                "axis": {"range": [0, 1], "tickwidth": 2},
                "bar": {"color": "#ff4444" if risk > threshold else "#00cc66"},
                "steps": [
                    {"range": [0, 0.3], "color": "#e8f5e9"},
                    {"range": [0.3, threshold], "color": "#fff9c4"},
                    {"range": [threshold, 1.0], "color": "#ffebee"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": threshold,
                },
            },
            title={"text": "Risk Score"},
        ))
        fig_gauge.update_layout(height=300, margin=dict(t=40, b=0, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Price Chart with Trade Markers ──
    st.divider()
    st.subheader("Price History & Trade Decisions")

    prices = [e["price"] for e in logs]
    cycles = [e["cycle"] for e in logs]
    blocked_cycles = [e["cycle"] for e in logs if not e["approved"]]
    blocked_prices = [e["price"] for e in logs if not e["approved"]]
    exec_buy_cycles = [e["cycle"] for e in logs if e["executed"] and e["signal"] == "BUY"]
    exec_buy_prices = [e["price"] for e in logs if e["executed"] and e["signal"] == "BUY"]
    exec_sell_cycles = [e["cycle"] for e in logs if e["executed"] and e["signal"] == "SELL"]
    exec_sell_prices = [e["price"] for e in logs if e["executed"] and e["signal"] == "SELL"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cycles, y=prices, mode="lines", name="BTC Price",
                             line=dict(color="#2196F3", width=2)))
    fig.add_trace(go.Scatter(x=blocked_cycles, y=blocked_prices, mode="markers", name="🚫 BLOCKED",
                             marker=dict(color="red", size=14, symbol="x")))
    fig.add_trace(go.Scatter(x=exec_buy_cycles, y=exec_buy_prices, mode="markers", name="✅ BUY",
                             marker=dict(color="green", size=10, symbol="triangle-up")))
    fig.add_trace(go.Scatter(x=exec_sell_cycles, y=exec_sell_prices, mode="markers", name="✅ SELL",
                             marker=dict(color="orange", size=10, symbol="triangle-down")))
    fig.update_layout(height=400, xaxis_title="Cycle", yaxis_title="Price (USDT)",
                      margin=dict(t=10, b=40, l=60, r=20))
    st.plotly_chart(fig, use_container_width=True)

    # ── Risk Score Timeline ──
    risk_scores = [e["risk_score"] for e in logs]
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Bar(x=cycles, y=risk_scores, name="Risk Score",
                              marker_color=["#ff4444" if r > threshold else "#00cc66" for r in risk_scores]))
    fig_risk.add_hline(y=threshold, line_dash="dash", line_color="red",
                       annotation_text=f"Threshold ({threshold})")
    fig_risk.update_layout(height=250, xaxis_title="Cycle", yaxis_title="Risk Score",
                           margin=dict(t=10, b=40, l=60, r=20))
    st.plotly_chart(fig_risk, use_container_width=True)

    # ── Trade Log Table ──
    st.divider()
    st.subheader("📋 Trade Decision Log")

    for entry in reversed(logs[-15:]):
        status_icon = "❌" if not entry["approved"] else ("✅" if entry["executed"] else "⏸")
        risk_color = "red" if entry["risk_score"] > threshold else "green"

        st.markdown(
            f"`Cycle {entry['cycle']}` | {status_icon} **{entry['signal']}** via "
            f"**{entry['strategy']}** | Price: ${entry['price']:,.2f} | "
            f"Risk: :{risk_color}[**{entry['risk_score']:.4f}**] | "
            f"{'**BLOCKED: ' + ', '.join(entry.get('reasons', [])) + '**' if not entry['approved'] else 'Approved'}"
        )

else:
    st.info("No trades yet. Click **Run Cycle** to start trading!")

# ── Auto-run ──
if auto_run:
    time.sleep(1.5)
    fetch("/run-cycle", method="POST")
    st.rerun()
