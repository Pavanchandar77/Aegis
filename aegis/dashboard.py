"""
AEGIS Dashboard - Clean Chart Section
Minimal, working charts for the risk governor dashboard.
"""
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(page_title="AEGIS", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.stApp { background: #0a0e17; color: #c4cad4; }
header[data-testid="stHeader"] { background: #0a0e17; }
.block-container { padding: 1rem 2rem 2rem 2rem; max-width: 100%; }
.js-plotly-plot .plotly .modebar { display: none !important; }
</style>""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────
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

def dark_fig(fig, h=200):
    fig.update_layout(
        plot_bgcolor="#0a0e17", paper_bgcolor="#0a0e17",
        font=dict(family="Inter, sans-serif", color="#6b7280", size=10),
        height=h, margin=dict(t=8, b=32, l=48, r=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6b7280", size=9)),
        xaxis=dict(gridcolor="#1a1f2e", zerolinecolor="#1a1f2e", tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#1a1f2e", zerolinecolor="#1a1f2e", tickfont=dict(size=9)),
    )
    return fig

# ─── Controls ────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
with col1:
    st.markdown("<h2 style='margin:0;color:#e2e8f0;'>AEGIS Risk Governor</h2>", unsafe_allow_html=True)
with col2:
    if st.button("Run Demo", use_container_width=True):
        post("/demo-scenario")
        st.rerun()
with col3:
    if st.button("Run Cycle", use_container_width=True):
        post("/run-cycle")
        st.rerun()
with col4:
    if st.button("Reset", use_container_width=True):
        post("/reset")
        st.rerun()
with col5:
    auto = st.toggle("Auto", value=False)

# ─── Data Fetch ──────────────────────────────────────────────────────────────
status = get("/status")
if "error" in status:
    st.error("API Offline - Start: python -m aegis.api")
    st.stop()

logs_data = get("/logs?last_n=50")
logs = logs_data.get("logs", [])

# ─── Metrics ─────────────────────────────────────────────────────────────────
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("BTC Price", f"${status.get('current_price', 0):,.2f}")
with m2:
    vol = (status.get('volatility') or 0) * 100
    st.metric("Volatility", f"{vol:.2f}%")
with m3:
    st.metric("Portfolio", f"${status.get('portfolio_value', 100000):,.2f}")
with m4:
    st.metric("P&L", f"${status.get('pnl', 0):,.2f}")
with m5:
    st.metric("Blocked", status.get('trades_blocked', 0))

# ─── CHARTS SECTION (CLEAN REWRITE) ──────────────────────────────────────────
st.markdown("---")
st.markdown("<h4 style='color:#6b7280;margin:10px 0;'>Performance Charts</h4>", unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Equity Curve
with chart_col1:
    st.markdown("<p style='color:#4b5563;font-size:12px;margin:0;'>Equity Curve</p>", unsafe_allow_html=True)
    
    perf = get("/performance-comparison")
    if perf and perf.get("with_aegis") and len(perf["with_aegis"]) > 1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=perf["cycles"], y=perf["with_aegis"],
            mode="lines", name="With AEGIS",
            line=dict(color="#22c55e", width=2)
        ))
        fig1.add_trace(go.Scatter(
            x=perf["cycles"], y=perf["without_aegis"],
            mode="lines", name="No Protection",
            line=dict(color="#ef4444", width=1.5, dash="dot")
        ))
        fig1 = dark_fig(fig1, 180)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Run demo to see equity curve")

# Chart 2: Price & Risk
with chart_col2:
    st.markdown("<p style='color:#4b5563;font-size:12px;margin:0;'>Price & Risk Score</p>", unsafe_allow_html=True)
    
    if logs:
        cycles = [e["cycle"] for e in logs]
        prices = [e["price"] for e in logs]
        risks = [e.get("risk_score", 0) * 100 for e in logs]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=cycles, y=prices, mode="lines", name="Price",
            line=dict(color="#3b82f6", width=1.5), yaxis="y"
        ))
        fig2.add_trace(go.Scatter(
            x=cycles, y=risks, mode="lines", name="Risk %",
            line=dict(color="#eab308", width=1, dash="dot"), yaxis="y2"
        ))
        
        fig2 = dark_fig(fig2, 180)
        fig2.update_layout(
            yaxis2=dict(overlaying="y", side="right", range=[0, 100], tickfont=dict(size=8)),
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No trade data yet")

# ─── Trade Log ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<h4 style='color:#6b7280;margin:10px 0;'>Recent Trades</h4>", unsafe_allow_html=True)

if logs:
    recent = list(reversed(logs[-10:]))
    for entry in recent:
        cycle = entry.get("cycle", 0)
        sig = entry.get("signal", "HOLD")
        approved = entry.get("approved", True)
        risk = entry.get("risk_score", 0) * 100
        price = entry.get("price", 0)
        
        status_color = "#22c55e" if approved else "#ef4444"
        status_text = "APPROVED" if approved else "BLOCKED"
        
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1a1f2e;font-size:12px;">
            <span style="color:#6b7280;">#{cycle:03d}</span>
            <span style="color:#e2e8f0;">{sig}</span>
            <span style="color:{status_color};">{status_text}</span>
            <span style="color:#6b7280;">Risk: {risk:.0f}</span>
            <span style="color:#6b7280;">${price:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No trades yet. Click 'Run Demo' to start.")

# ─── Auto Run ────────────────────────────────────────────────────────────────
if auto:
    import time
    time.sleep(2)
    post("/run-cycle")
    st.rerun()
