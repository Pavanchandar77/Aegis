"""
<<<<<<< HEAD
AEGIS — Hackathon-Winning Premium Dashboard v3
Dramatic visuals, glassmorphism, neon accents, animated pipeline.
=======
AEGIS — Institutional Risk Governor Dashboard
Bloomberg-meets-Linear design. Dense, functional, zero fluff.
>>>>>>> b1f637b8c3b768909d03cafb1212e9e197c1b03c
"""
import streamlit as st
import requests, time, random
import plotly.graph_objects as go
<<<<<<< HEAD

API = "http://localhost:8000"
st.set_page_config(page_title="AEGIS Risk Governor", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# ━━━━━━━━━━ ULTRA-PREMIUM CSS ━━━━━━━━━━
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif}
.stApp{background:#05080f;color:#e0e6ed}
header[data-testid="stHeader"]{background:#05080f}
.block-container{padding-top:1.2rem;max-width:1400px}
h1,h2,h3,h4,h5,h6,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{color:#fff!important;font-family:'Outfit',sans-serif!important}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{box-shadow:0 0 15px rgba(99,102,241,.15)}50%{box-shadow:0 0 35px rgba(99,102,241,.35)}}
@keyframes pulseR{0%,100%{box-shadow:0 0 25px rgba(239,68,68,.2),inset 0 0 30px rgba(239,68,68,.05)}50%{box-shadow:0 0 60px rgba(239,68,68,.45),inset 0 0 40px rgba(239,68,68,.08)}}
@keyframes pulseG{0%,100%{box-shadow:0 0 20px rgba(16,185,129,.15)}50%{box-shadow:0 0 45px rgba(16,185,129,.3)}}
@keyframes pulseA{0%,100%{box-shadow:0 0 20px rgba(245,158,11,.12)}50%{box-shadow:0 0 45px rgba(245,158,11,.28)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes slideL{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}
@keyframes orbit{0%{left:-8px;opacity:0}15%{opacity:1}85%{opacity:1}100%{left:calc(100% + 8px);opacity:0}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes borderShift{0%{border-color:#6366f1}33%{border-color:#8b5cf6}66%{border-color:#3b82f6}100%{border-color:#6366f1}}

/* Hero */
.hero{background:linear-gradient(135deg,#0a0e1a 0%,#131640 40%,#1a0a2e 70%,#0a0e1a 100%);border:1px solid #1e1b4b;border-radius:20px;padding:28px 36px;margin-bottom:20px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-60%;right:-30%;width:80%;height:200%;background:radial-gradient(ellipse,rgba(99,102,241,.07) 0%,transparent 70%)}
.hero::after{content:'';position:absolute;bottom:-60%;left:-20%;width:60%;height:180%;background:radial-gradient(ellipse,rgba(139,92,246,.05) 0%,transparent 70%)}
.hero-t{font-size:44px;font-weight:900;letter-spacing:-1.5px;margin:0;background:linear-gradient(135deg,#818cf8,#c084fc,#60a5fa,#818cf8);background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 4s linear infinite;position:relative;font-family:'Outfit',sans-serif}
.hero-s{font-size:14px;color:#94a3b8;margin-top:4px;position:relative;letter-spacing:.3px}

/* Cards */
.gc{background:linear-gradient(135deg,rgba(15,23,42,.9),rgba(30,27,75,.4));backdrop-filter:blur(20px);border:1px solid rgba(99,102,241,.15);border-radius:16px;padding:22px;text-align:center;transition:all .35s cubic-bezier(.4,0,.2,1);animation:fadeUp .5s ease-out}
.gc:hover{border-color:rgba(99,102,241,.4);transform:translateY(-3px);box-shadow:0 12px 40px rgba(99,102,241,.12)}
.gl{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#64748b;margin-bottom:6px}
.gv{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:#f8fafc}
.gv.g{color:#10b981}.gv.r{color:#ef4444}.gv.b{color:#818cf8}.gv.a{color:#f59e0b}

/* Pipeline */
.pipe{display:flex;align-items:center;justify-content:center;gap:0;padding:18px 24px;margin-bottom:20px;background:linear-gradient(135deg,rgba(10,14,26,.95),rgba(19,22,64,.5),rgba(10,14,26,.95));border:1px solid rgba(99,102,241,.12);border-radius:16px;animation:fadeUp .5s ease-out;position:relative;overflow:hidden}
.pn{display:flex;flex-direction:column;align-items:center;padding:14px 24px;border-radius:14px;z-index:2;transition:all .3s;animation:float 3s ease-in-out infinite}
.pn-i{font-size:26px;margin-bottom:4px}.pn-l{font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase}.pn-s{font-size:9px;color:#64748b;margin-top:2px}
.pn.ag{background:linear-gradient(135deg,rgba(59,130,246,.1),rgba(59,130,246,.05));border:1px solid rgba(59,130,246,.3);animation-delay:0s}
.pn.ae{background:linear-gradient(135deg,rgba(99,102,241,.15),rgba(139,92,246,.1));border:2px solid rgba(129,140,248,.5);animation:glow 2.5s ease-in-out infinite,float 3s ease-in-out infinite;animation-delay:.3s;padding:18px 32px}
.pn.ex{background:linear-gradient(135deg,rgba(16,185,129,.1),rgba(16,185,129,.05));border:1px solid rgba(16,185,129,.3);animation-delay:.6s}
.pn.bk{background:linear-gradient(135deg,rgba(239,68,68,.1),rgba(239,68,68,.05));border:1px solid rgba(239,68,68,.4)}
.pa{position:relative;width:70px;height:3px;background:linear-gradient(90deg,transparent,rgba(99,102,241,.4),transparent);margin:0 6px;z-index:1}
.pa::after{content:'';position:absolute;right:-5px;width:10px;height:10px;border-right:2px solid #818cf8;border-top:2px solid #818cf8;transform:rotate(45deg);top:-4px}
.pd{position:absolute;width:6px;height:6px;background:#818cf8;border-radius:50%;animation:orbit 2s ease-in-out infinite;box-shadow:0 0 8px #818cf8}

/* Decision */
.db{background:linear-gradient(135deg,#1a0505,#2d0808,#3d0a0a);border:1px solid rgba(239,68,68,.5);border-radius:16px;padding:24px;text-align:center;animation:pulseR 2s ease-in-out infinite,fadeUp .5s ease-out;position:relative;overflow:hidden}
.db::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 0%,rgba(239,68,68,.08),transparent 60%)}
.de{background:linear-gradient(135deg,#021a0a,#04301a,#064e2a);border:1px solid rgba(16,185,129,.4);border-radius:16px;padding:24px;text-align:center;animation:pulseG 2.5s ease-in-out infinite,fadeUp .5s ease-out;position:relative;overflow:hidden}
.de::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 0%,rgba(16,185,129,.06),transparent 60%)}
.dh{background:linear-gradient(135deg,rgba(15,23,42,.9),rgba(30,41,59,.5));border:1px solid rgba(71,85,105,.3);border-radius:16px;padding:24px;text-align:center;animation:fadeUp .5s ease-out}
.dt{font-size:28px;font-weight:900;letter-spacing:4px;font-family:'Outfit',sans-serif}
.dr{font-size:12px;margin-top:8px;font-weight:500;line-height:1.5}

/* What-If */
.wc{border-radius:16px;padding:22px;position:relative;overflow:hidden;animation:fadeUp .6s ease-out;transition:all .35s}
.wc:hover{transform:translateY(-3px)}
.wa{background:linear-gradient(135deg,rgba(4,30,15,.9),rgba(6,50,30,.6));border:1px solid rgba(16,185,129,.3)}
.wa:hover{border-color:rgba(16,185,129,.6);box-shadow:0 8px 30px rgba(16,185,129,.12)}
.wb{background:linear-gradient(135deg,rgba(30,8,8,.9),rgba(50,12,12,.6));border:1px solid rgba(239,68,68,.3)}
.wb:hover{border-color:rgba(239,68,68,.6);box-shadow:0 8px 30px rgba(239,68,68,.12)}
.wt{font-size:12px;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,.06)}
.wr{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.03)}
.wl{font-size:11px;color:#94a3b8;font-weight:500}.wv{font-size:16px;font-weight:800;font-family:'JetBrains Mono',monospace}

/* Agent Leaderboard */
.ar{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,rgba(15,23,42,.8),rgba(30,27,75,.25));border:1px solid rgba(99,102,241,.1);border-radius:12px;padding:12px 18px;margin:6px 0;transition:all .35s;animation:slideL .4s ease-out}
.ar:hover{border-color:rgba(99,102,241,.35);transform:translateX(6px);box-shadow:0 4px 25px rgba(99,102,241,.1)}
.ark{font-size:20px;font-weight:900;color:#818cf8;font-family:'JetBrains Mono',monospace;min-width:32px}
.arn{font-size:14px;font-weight:700;color:#f8fafc;min-width:120px}
.ars{text-align:center;min-width:70px}.arv{font-size:16px;font-weight:800;font-family:'JetBrains Mono',monospace}.arl{font-size:8px;font-weight:700;letter-spacing:1.5px;color:#64748b;text-transform:uppercase}
.badge{padding:3px 12px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1px}
.b-ok{background:rgba(16,185,129,.12);color:#10b981;border:1px solid rgba(16,185,129,.3)}
.b-rr{background:rgba(245,158,11,.12);color:#f59e0b;border:1px solid rgba(245,158,11,.3)}
.b-fl{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.3)}
.tb{width:100%;height:5px;background:rgba(30,41,59,.6);border-radius:3px;overflow:hidden;margin-top:3px}
.tf{height:100%;border-radius:3px;transition:width .8s ease-out}

/* Signal Bars */
.sbc{margin:6px 0;animation:fadeUp .5s ease-out}
.sbl{font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;display:flex;justify-content:space-between}
.sbt{width:100%;height:8px;background:rgba(30,41,59,.6);border-radius:4px;overflow:hidden}
.sbf{height:100%;border-radius:4px;transition:width 1s cubic-bezier(.4,0,.2,1)}

/* Enforcement */
.ec{border-radius:12px;padding:14px 18px;margin:6px 0;animation:slideL .35s ease-out;transition:all .3s;position:relative}
.ec:hover{transform:translateX(4px)}
.ec-b{background:linear-gradient(95deg,rgba(239,68,68,.06),rgba(15,23,42,.8) 40%);border-left:3px solid #ef4444}
.ec-g{background:linear-gradient(95deg,rgba(16,185,129,.06),rgba(15,23,42,.8) 40%);border-left:3px solid #10b981}
.ec-h{background:rgba(15,23,42,.6);border-left:3px solid #475569}
.es{font-size:12px;font-weight:800;letter-spacing:1.5px}
.ed{font-size:11px;color:#94a3b8;margin-top:4px;font-family:'JetBrains Mono',monospace}
.er{font-size:10px;margin-top:5px;padding:4px 10px;background:rgba(239,68,68,.06);border-radius:6px;color:#fca5a5;font-weight:500}

/* Section header */
.sh{font-size:11px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#818cf8;margin:24px 0 12px 0;padding-bottom:7px;border-bottom:1px solid rgba(99,102,241,.15);animation:fadeUp .4s ease-out}

/* Badges */
.vb{display:inline-block;padding:3px 12px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1px}
.vl{background:rgba(16,185,129,.1);color:#10b981;border:1px solid rgba(16,185,129,.3)}
.vm{background:rgba(245,158,11,.1);color:#f59e0b;border:1px solid rgba(245,158,11,.3)}
.vh{background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.3)}

/* Buttons */
.stButton>button{border-radius:12px;font-weight:600;font-family:'Inter',sans-serif;letter-spacing:.5px;transition:all .3s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(99,102,241,.2)}
.js-plotly-plot .plotly .modebar{display:none!important}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:28px!important;color:#f8fafc!important}
</style>""", unsafe_allow_html=True)

# ━━━━ HELPERS ━━━━
def api(ep, m="GET"):
    try:
        r = (requests.post if m == "POST" else requests.get)(f"{API}{ep}", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def pdark(fig, h=320):
    fig.update_layout(plot_bgcolor="#05080f", paper_bgcolor="#05080f",
        font=dict(family="Inter", color="#94a3b8"), height=h,
        margin=dict(t=20,b=40,l=50,r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        xaxis=dict(gridcolor="#111827", zerolinecolor="#111827"),
        yaxis=dict(gridcolor="#111827", zerolinecolor="#111827"))
    return fig

# ━━━━ HERO ━━━━
st.markdown("""<div class="hero">
<div class="hero-t">AEGIS</div>
<div class="hero-s">Autonomous Risk Governor — Deterministic AI-powered trade firewall protecting capital in real-time</div>
</div>""", unsafe_allow_html=True)

# ━━━━ CONTROLS ━━━━
c1,c2,c3,c4,c5,c6 = st.columns([2,2,1.5,1.5,1.3,1])
with c1: demo = st.button("🚀 RUN DEMO SCENARIO", use_container_width=True, type="primary")
with c2: risk = st.button("⚡ RUN RISK SCENARIO", use_container_width=True)
with c3: cyc = st.button("▶ Single Cycle", use_container_width=True)
with c4: vol = st.button("🌊 Vol Spike", use_container_width=True)
with c5: rst = st.button("🔄 Reset", use_container_width=True)
with c6: auto = st.toggle("Auto", value=False)
=======
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
>>>>>>> b1f637b8c3b768909d03cafb1212e9e197c1b03c

if demo:
    with st.spinner("Running demo..."): api("/demo-scenario","POST")
if risk:
    with st.spinner("Running risk scenario..."):
        api("/set-volatile?volatile=false","POST"); api("/run-cycle","POST"); api("/run-cycle","POST")
        api("/set-volatile?volatile=true","POST"); api("/run-cycle","POST"); api("/run-cycle","POST"); api("/run-cycle","POST")
if cyc: api("/run-cycle","POST")
if vol: api("/set-volatile?volatile=true","POST")
if rst: api("/reset","POST"); st.rerun()

<<<<<<< HEAD
# ━━━━ FETCH ━━━━
status = api("/status")
if "error" in status:
    st.markdown("""<div style="text-align:center;padding:80px 20px;animation:fadeUp .8s">
    <div style="font-size:64px;margin-bottom:20px">🛡️</div>
    <div style="font-size:24px;color:#ef4444;font-weight:700">AEGIS API Offline</div>
    <div style="color:#64748b;margin-top:12px">Start: <code style="color:#818cf8">python -m aegis.api</code></div>
    </div>""", unsafe_allow_html=True); st.stop()

ld = api("/logs?last_n=50"); logs = ld.get("logs",[]); latest = logs[-1] if logs else None
thr = status.get("risk_threshold", 0.65)

# ━━━━ PIPELINE ━━━━
ec = "ex"; ei = "🎯"; el = "EXECUTION"; es = "Trade deployed"
if latest:
    if not latest["approved"]: ec,ei,el,es = "bk","🚫","BLOCKED","Trade rejected"
    elif latest.get("executed") and latest["signal"]!="HOLD": es = f"{latest['signal']} executed"

st.markdown(f"""<div class="pipe">
<div class="pn ag"><div class="pn-i">🤖</div><div class="pn-l" style="color:#60a5fa">TRADING AGENTS</div><div class="pn-s">Strategy signals</div></div>
<div class="pa"><div class="pd"></div></div>
<div class="pn ae"><div class="pn-i">🛡️</div><div class="pn-l" style="color:#a78bfa">AEGIS ENGINE</div><div class="pn-s" style="color:#c4b5fd">Risk evaluation</div></div>
<div class="pa"><div class="pd" style="animation-delay:.6s"></div></div>
<div class="pn {ec}"><div class="pn-i">{ei}</div><div class="pn-l" style="color:{'#ef4444' if ec=='bk' else '#10b981'}">{el}</div><div class="pn-s">{es}</div></div>
</div>""", unsafe_allow_html=True)

# ━━━━ METRICS ━━━━
price = status.get("current_price",0) or 0; vl = status.get("volatility",0) or 0; vp = vl*100
vbg = f'<span class="vb vh">EXTREME</span>' if vp>2 else f'<span class="vb vm">ELEVATED</span>' if vp>.8 else f'<span class="vb vl">NORMAL</span>'

m1,m2,m3,m4,m5,m6 = st.columns(6)
with m1: st.markdown(f'<div class="gc"><div class="gl">BTC / USDT</div><div class="gv b">${price:,.2f}</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="gc"><div class="gl">Volatility</div><div class="gv {"r" if vp>2 else "a" if vp>.8 else "g"}">{vp:.2f}%</div><div style="margin-top:6px">{vbg}</div></div>', unsafe_allow_html=True)
with m3:
    pnl = status.get("pnl",0) or 0
    st.markdown(f'<div class="gc"><div class="gl">Portfolio P&L</div><div class="gv {"g" if pnl>=0 else "r"}">{"+" if pnl>=0 else ""}${pnl:,.2f}</div></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="gc"><div class="gl">Portfolio Value</div><div class="gv">${status.get("portfolio_value",100000) or 100000:,.2f}</div></div>', unsafe_allow_html=True)
with m5: st.markdown(f'<div class="gc"><div class="gl">Trades Blocked</div><div class="gv r">{status.get("trades_blocked",0)}</div></div>', unsafe_allow_html=True)
with m6: st.markdown(f'<div class="gc"><div class="gl">Trades Approved</div><div class="gv g">{status.get("trades_approved",0)}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ━━━━ MAIN PANELS ━━━━
if latest:
    risk_val = latest["risk_score"]; r100 = round(risk_val*100)
    cD, cG, cS = st.columns([2,1.5,1.5])

    # Decision Panel
    with cD:
        st.markdown('<div class="sh">🔥 TRADE DECISION</div>', unsafe_allow_html=True)
        if not latest["approved"]:
            reasons = latest.get("reasons",["Risk threshold exceeded"])
            rh = "".join(f'<div class="er">⛔ {r}</div>' for r in reasons)
            cap = latest["price"]*0.1
            st.markdown(f"""<div class="db"><div style="font-size:40px;margin-bottom:4px;position:relative">🚨</div>
            <div class="dt" style="color:#ef4444">TRADE BLOCKED</div>
            <div class="dr" style="color:#fca5a5">{latest['strategy']} — {latest['signal']} @ ${latest['price']:,.2f}</div>
            <div style="margin-top:10px;text-align:left">{rh}</div>
            <div style="margin-top:12px;padding:8px 16px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:8px;display:inline-block">
            <span style="color:#10b981;font-weight:700;font-size:12px">🛡️ AEGIS protected ${cap:,.2f} in capital</span></div></div>""", unsafe_allow_html=True)
        elif latest.get("executed") and latest["signal"]!="HOLD":
            st.markdown(f"""<div class="de"><div style="font-size:40px;margin-bottom:4px;position:relative">✅</div>
            <div class="dt" style="color:#10b981">TRADE APPROVED</div>
            <div style="color:#6ee7b7;margin-top:6px;font-size:13px;font-weight:600">{latest['signal']} via {latest['strategy']} @ ${latest['price']:,.2f}</div>
            <div style="margin-top:8px;padding:6px 12px;background:rgba(16,185,129,.08);border-radius:8px;display:inline-block">
            <span style="color:#6ee7b7;font-size:11px">Risk: {r100} — Safe ✓</span></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="dh"><div style="font-size:40px;margin-bottom:4px">⏸️</div>
            <div class="dt" style="color:#64748b">HOLDING</div>
            <div style="color:#94a3b8;margin-top:6px;font-size:13px">No action — market stable</div></div>""", unsafe_allow_html=True)

    # Risk Gauge
    with cG:
        st.markdown('<div class="sh">RISK FIREWALL</div>', unsafe_allow_html=True)
        bc = "#ef4444" if risk_val>thr else "#f59e0b" if risk_val>.4 else "#10b981"
        fg = go.Figure(go.Indicator(mode="gauge+number", value=r100,
            number={"suffix":"","font":{"size":48,"color":bc,"family":"JetBrains Mono"}},
            gauge={"axis":{"range":[0,100],"tickwidth":0,"tickfont":{"color":"#475569","size":9}},
                "bar":{"color":bc,"thickness":.8},"bgcolor":"#111827","borderwidth":0,
                "steps":[{"range":[0,35],"color":"rgba(16,185,129,.06)"},{"range":[35,65],"color":"rgba(245,158,11,.06)"},{"range":[65,100],"color":"rgba(239,68,68,.08)"}],
                "threshold":{"line":{"color":"#ef4444","width":3},"thickness":.8,"value":thr*100}}))
        fg.update_layout(plot_bgcolor="#05080f",paper_bgcolor="#05080f",height=240,margin=dict(t=20,b=0,l=20,r=20),
            annotations=[dict(text=f"Threshold: {thr*100:.0f}",x=.5,y=-.05,showarrow=False,font=dict(size=10,color="#ef4444",family="JetBrains Mono"))])
        st.plotly_chart(fg, use_container_width=True)

    # Multi-Signal Display
    with cS:
        st.markdown('<div class="sh">🎯 DECISION SIGNALS</div>', unsafe_allow_html=True)
        dr = r100; mf = min(100,max(5,round(vp*20+random.uniform(-5,10)))); ac = round(latest["confidence"]*100)
        dc = "#ef4444" if dr>65 else "#f59e0b" if dr>40 else "#10b981"
        mc = "#ef4444" if mf>60 else "#f59e0b" if mf>35 else "#10b981"
        st.markdown(f"""<div class="gc" style="padding:18px;text-align:left">
        <div class="sbc"><div class="sbl"><span>Deterministic Risk <span style="color:#f59e0b">(PRIMARY)</span></span><span style="color:{dc};font-weight:800">{dr}%</span></div>
        <div class="sbt"><div class="sbf" style="width:{dr}%;background:linear-gradient(90deg,{dc},{dc}88)"></div></div></div>
        <div class="sbc" style="margin-top:12px"><div class="sbl"><span>Market Condition</span><span style="color:{mc};font-weight:800">{mf}%</span></div>
        <div class="sbt"><div class="sbf" style="width:{mf}%;background:linear-gradient(90deg,{mc},{mc}88)"></div></div></div>
        <div class="sbc" style="margin-top:12px"><div class="sbl"><span>AI Confidence <span style="color:#64748b">(ADVISORY)</span></span><span style="color:#818cf8;font-weight:800">{ac}%</span></div>
        <div class="sbt"><div class="sbf" style="width:{ac}%;background:linear-gradient(90deg,#818cf8,#818cf888)"></div></div></div>
        <div style="margin-top:14px;padding:6px 10px;background:rgba(245,158,11,.06);border-radius:6px;border:1px solid rgba(245,158,11,.15)">
        <span style="font-size:9px;color:#f59e0b;font-weight:700;letter-spacing:1px">⚠️ AI ASSISTS — DOES NOT DECIDE. DETERMINISTIC RULES ARE PRIMARY.</span></div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ━━━━ WHAT-IF SIMULATOR ━━━━
    st.markdown('<div class="sh">🔮 WHAT-IF SIMULATOR — TRADE IMPACT ANALYSIS</div>', unsafe_allow_html=True)
    wf = api("/what-if")
    if wf.get("available"):
        ia = wf["if_allowed"]; ib = wf["if_blocked"]
        w1,w2 = st.columns(2)
        with w1:
            st.markdown(f"""<div class="wc wa">
            <div class="wt" style="color:#10b981">✅ IF TRADE ALLOWED</div>
            <div class="wr"><span class="wl">Expected Return</span><span class="wv" style="color:#10b981">+{ia['expected_return_pct']}%</span></div>
            <div class="wr"><span class="wl">Worst-Case Loss</span><span class="wv" style="color:#ef4444">-{ia['worst_case_loss_pct']}%</span></div>
            <div class="wr"><span class="wl">Drawdown Impact</span><span class="wv" style="color:#f59e0b">{ia['drawdown_impact_pct']}%</span></div>
            <div class="wr" style="border:none"><span class="wl">Volatility Exposure</span><span class="wv" style="color:#94a3b8">{ia['volatility_exposure_pct']}%</span></div></div>""", unsafe_allow_html=True)
        with w2:
            st.markdown(f"""<div class="wc wb">
            <div class="wt" style="color:#ef4444">🚫 IF TRADE BLOCKED</div>
            <div class="wr"><span class="wl">Loss Avoided</span><span class="wv" style="color:#10b981">₹{ib['loss_avoided']:,.2f}</span></div>
            <div class="wr"><span class="wl">Capital Preserved</span><span class="wv" style="color:#818cf8">₹{ib['capital_preserved']:,.2f}</span></div>
            <div class="wr" style="border:none"><span class="wl">Missed Upside</span><span class="wv" style="color:#f59e0b">+{ib['missed_upside_pct']}%</span></div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ━━━━ CHARTS ━━━━
    ch1,ch2 = st.columns(2)
    cycles = [e["cycle"] for e in logs]; prices = [e["price"] for e in logs]
    with ch1:
        st.markdown('<div class="sh">PRICE ACTION & TRADE DECISIONS</div>', unsafe_allow_html=True)
        f1 = go.Figure()
        f1.add_trace(go.Scatter(x=cycles,y=prices,mode="lines",name="BTC",line=dict(color="#818cf8",width=2),fill="tozeroy",fillcolor="rgba(99,102,241,.04)"))
        f1.add_trace(go.Scatter(x=[e["cycle"] for e in logs if not e["approved"]],y=[e["price"] for e in logs if not e["approved"]],mode="markers",name="BLOCKED",marker=dict(color="#ef4444",size=13,symbol="x",line=dict(width=2,color="#ef4444"))))
        f1.add_trace(go.Scatter(x=[e["cycle"] for e in logs if e["executed"] and e["signal"]=="BUY"],y=[e["price"] for e in logs if e["executed"] and e["signal"]=="BUY"],mode="markers",name="BUY",marker=dict(color="#10b981",size=9,symbol="triangle-up")))
        f1.add_trace(go.Scatter(x=[e["cycle"] for e in logs if e["executed"] and e["signal"]=="SELL"],y=[e["price"] for e in logs if e["executed"] and e["signal"]=="SELL"],mode="markers",name="SELL",marker=dict(color="#f59e0b",size=9,symbol="triangle-down")))
        st.plotly_chart(pdark(f1,220), use_container_width=True)
    with ch2:
        st.markdown('<div class="sh">RISK SCORE TIMELINE</div>', unsafe_allow_html=True)
        rs = [e["risk_score"]*100 for e in logs]
        cs = ["#ef4444" if r>thr*100 else "#f59e0b" if r>40 else "#10b981" for r in rs]
        f2 = go.Figure(go.Bar(x=cycles,y=rs,marker_color=cs,marker_line=dict(width=0)))
        f2.add_hline(y=thr*100,line_dash="dot",line_color="#ef4444",line_width=2,annotation_text=f"BLOCK ({thr*100:.0f})",annotation_font=dict(color="#ef4444",size=10),annotation_position="top left")
        f2 = pdark(f2,220); f2.update_yaxes(range=[0,105])
        st.plotly_chart(f2, use_container_width=True)

    # ━━━━ LEADERBOARD + PERF ━━━━
    lb_c, pf_c = st.columns([1.2,1])
    with lb_c:
        st.markdown('<div class="sh">🏆 AGENT LEADERBOARD</div>', unsafe_allow_html=True)
        lb = api("/agent-leaderboard"); agents = lb.get("agents",[])
        for i,a in enumerate(agents):
            tc = "#10b981" if a["trust_score"]>=70 else "#f59e0b" if a["trust_score"]>=40 else "#ef4444"
            rc = "#ef4444" if a["risk_score"]>50 else "#f59e0b" if a["risk_score"]>30 else "#10b981"
            bc = "b-ok" if a["status"]=="Approved" else "b-rr" if a["status"]=="Restricted" else "b-fl"
            st.markdown(f"""<div class="ar" style="animation-delay:{i*.08}s">
            <div class="ark">#{i+1}</div><div class="arn">🤖 {a['name']}</div>
            <div class="ars"><div class="arv" style="color:{tc}">{a['trust_score']}</div><div class="arl">Trust</div>
            <div class="tb"><div class="tf" style="width:{a['trust_score']}%;background:{tc}"></div></div></div>
            <div class="ars"><div class="arv" style="color:{rc}">{a['risk_score']}</div><div class="arl">Risk</div></div>
            <div class="ars"><div class="arv" style="color:#818cf8">{a['win_rate']}%</div><div class="arl">Win</div></div>
            <div class="ars"><div class="arv" style="color:#94a3b8">{a['trades']}</div><div class="arl">Trades</div></div>
            <div><span class="badge {bc}">{a['status'].upper()}</span></div></div>""", unsafe_allow_html=True)

    with pf_c:
        perf = api("/performance-comparison")
        if perf.get("with_aegis") and len(perf["with_aegis"])>2:
            st.markdown('<div class="sh">AEGIS vs NO AEGIS</div>', unsafe_allow_html=True)
            fp = go.Figure()
            fp.add_trace(go.Scatter(x=perf["cycles"],y=perf["without_aegis"],mode="lines",name="Without AEGIS",line=dict(color="#ef4444",width=2,dash="dash"),fill="tozeroy",fillcolor="rgba(239,68,68,.03)"))
            fp.add_trace(go.Scatter(x=perf["cycles"],y=perf["with_aegis"],mode="lines",name="With AEGIS",line=dict(color="#10b981",width=3),fill="tozeroy",fillcolor="rgba(16,185,129,.04)"))
            fp = pdark(fp,260); fp.update_layout(legend=dict(x=.02,y=.98,font=dict(size=11)))
            st.plotly_chart(fp, use_container_width=True)
            sv = perf["with_aegis"][-1] - perf["without_aegis"][-1]
            st.markdown(f'<div class="gc" style="padding:14px"><div class="gl">Capital Saved by AEGIS</div><div class="gv g" style="font-size:22px">+${max(sv,0):,.2f}</div></div>', unsafe_allow_html=True)

    # ━━━━ ENFORCEMENT LOG ━━━━
    st.markdown('<div class="sh">📋 REAL-TIME ENFORCEMENT LOG</div>', unsafe_allow_html=True)
    for e in reversed(logs[-12:]):
        r = round(e["risk_score"]*100); rc = "#ef4444" if r>65 else "#f59e0b" if r>40 else "#10b981"
        if not e["approved"]:
            rns = " · ".join(e.get("reasons",[])) or "Risk exceeded"
            st.markdown(f"""<div class="ec ec-b"><div style="display:flex;justify-content:space-between;align-items:center">
            <div><span class="es" style="color:#ef4444">🚫 BLOCKED</span><span style="color:#475569;margin-left:10px;font-size:11px">#{e['cycle']:03d}</span></div>
            <span style="color:{rc};font-weight:800;font-family:'JetBrains Mono',monospace;font-size:12px">RISK: {r}</span></div>
            <div class="ed">{e['strategy']} → {e['signal']} @ ${e['price']:,.2f}</div>
            <div class="er">⛔ {rns}</div></div>""", unsafe_allow_html=True)
        elif e["executed"] and e["signal"]!="HOLD":
            st.markdown(f"""<div class="ec ec-g"><div style="display:flex;justify-content:space-between;align-items:center">
            <div><span class="es" style="color:#10b981">✅ APPROVED</span><span style="color:#475569;margin-left:10px;font-size:11px">#{e['cycle']:03d}</span></div>
            <span style="color:{rc};font-weight:800;font-family:'JetBrains Mono',monospace;font-size:12px">RISK: {r}</span></div>
            <div class="ed">{e['strategy']} → {e['signal']} @ ${e['price']:,.2f}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="ec ec-h"><div style="display:flex;justify-content:space-between;align-items:center">
            <div><span class="es" style="color:#64748b">⏸️ HOLD</span><span style="color:#475569;margin-left:10px;font-size:11px">#{e['cycle']:03d}</span></div>
            <span style="color:{rc};font-weight:800;font-family:'JetBrains Mono',monospace;font-size:12px">RISK: {r}</span></div>
            <div class="ed">{e['strategy']} @ ${e['price']:,.2f}</div></div>""", unsafe_allow_html=True)

else:
    st.markdown("""<div style="text-align:center;padding:80px 20px;animation:fadeUp .8s ease-out">
    <div style="font-size:80px;margin-bottom:16px;animation:float 3s ease-in-out infinite">🛡️</div>
    <div style="font-size:32px;font-weight:800;font-family:'Outfit',sans-serif;background:linear-gradient(135deg,#818cf8,#c084fc,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent">AEGIS Ready</div>
    <div style="color:#64748b;margin-top:12px;font-size:15px">Click <b style="color:#818cf8">RUN DEMO SCENARIO</b> or <b style="color:#f59e0b">RUN RISK SCENARIO</b> to watch AEGIS protect capital</div>
    </div>""", unsafe_allow_html=True)

# ━━━━ AUTO-RUN ━━━━
if auto:
    time.sleep(1.5); api("/run-cycle","POST"); st.rerun()
=======
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
>>>>>>> b1f637b8c3b768909d03cafb1212e9e197c1b03c
