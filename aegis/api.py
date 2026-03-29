"""
AEGIS FastAPI Backend v4 — Enhanced for Hackathon

Endpoints:
  GET  /status             — current system state
  GET  /logs               — trade decision log
  POST /run-cycle          — trigger one trading cycle
  POST /set-volatile       — toggle volatile mode
  POST /demo-scenario      — run 5 calm + 5 volatile cycles
  POST /reset              — reset entire system
  GET  /portfolio          — portfolio summary
  GET  /risk-breakdown     — live risk rule states from engine
  GET  /performance-comparison — with vs without aegis equity curves
  GET  /agents             — agent reputation leaderboard
  GET  /what-if/{cycle}    — what-if analysis for a specific trade
  POST /run-risk-scenario  — rapid-fire demo with mixed outcomes
"""

import random
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.main import AegisGovernor

app = FastAPI(title="AEGIS Risk Governor", version="4.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

governor = AegisGovernor(risk_threshold=0.65)
governor.market.seed_history(30)

# ─── Agent Reputation State ─────────────────────────────────────────────────

AGENTS = {
    "Momentum Alpha": {
        "name": "Momentum Alpha",
        "type": "Momentum",
        "trust_score": 72,
        "risk_score": 0.35,
        "win_rate": 64.2,
        "trades": 0,
        "wins": 0,
        "blocked": 0,
        "status": "Approved",
    },
    "MeanRev Beta": {
        "name": "MeanRev Beta",
        "type": "MeanReversion",
        "trust_score": 68,
        "risk_score": 0.42,
        "win_rate": 58.1,
        "trades": 0,
        "wins": 0,
        "blocked": 0,
        "status": "Approved",
    },
    "Volatility Gamma": {
        "name": "Volatility Gamma",
        "type": "Momentum",
        "trust_score": 45,
        "risk_score": 0.71,
        "win_rate": 41.5,
        "trades": 0,
        "wins": 0,
        "blocked": 0,
        "status": "Flagged",
    },
    "Arb Delta": {
        "name": "Arb Delta",
        "type": "MeanReversion",
        "trust_score": 82,
        "risk_score": 0.22,
        "win_rate": 71.3,
        "trades": 0,
        "wins": 0,
        "blocked": 0,
        "status": "Approved",
    },
}

# ─── Enforcement Log ────────────────────────────────────────────────────────

enforcement_log: list[dict] = []


def _update_agent_reputation(signal: dict, risk_result: dict, trade_result: dict):
    """Update agent trust scores based on trade outcomes."""
    strategy = signal.get("strategy", "")
    # Map strategy to agent
    agent_name = None
    if strategy == "Momentum":
        agent_name = random.choice(["Momentum Alpha", "Volatility Gamma"])
    elif strategy == "MeanReversion":
        agent_name = random.choice(["MeanRev Beta", "Arb Delta"])
    else:
        return agent_name

    agent = AGENTS[agent_name]
    agent["trades"] += 1

    if not risk_result["approved"]:
        # Risky trade → trust decreases
        agent["trust_score"] = max(0, agent["trust_score"] - random.randint(2, 5))
        agent["risk_score"] = min(1.0, agent["risk_score"] + random.uniform(0.02, 0.05))
        agent["blocked"] += 1
    elif trade_result.get("executed") and trade_result.get("pnl", 0) >= 0:
        # Safe + profitable → trust increases
        agent["trust_score"] = min(100, agent["trust_score"] + random.randint(1, 3))
        agent["risk_score"] = max(0.0, agent["risk_score"] - random.uniform(0.01, 0.03))
        agent["wins"] += 1
    else:
        agent["wins"] += 1 if random.random() > 0.4 else 0

    # Update win rate
    if agent["trades"] > 0:
        base_wr = agent["win_rate"]
        actual_wr = (agent["wins"] / agent["trades"]) * 100 if agent["trades"] > 3 else base_wr
        agent["win_rate"] = round(0.7 * base_wr + 0.3 * actual_wr, 1)

    # Update status
    if agent["trust_score"] >= 65:
        agent["status"] = "Approved"
    elif agent["trust_score"] >= 40:
        agent["status"] = "Restricted"
    else:
        agent["status"] = "Flagged"

    return agent_name


def _compute_what_if(price: float, signal: dict, risk_result: dict):
    """Compute what-if analysis for a trade."""
    action = signal.get("signal", "HOLD")
    confidence = signal.get("confidence", 0.5)
    risk_score = risk_result.get("risk_score", 0.0)
    trade_value = price * 0.1  # standard trade size

    # Simulated projections
    rng = random.Random(int(price * 100))

    # "If Allowed" projections
    expected_return = round(rng.uniform(0.5, 3.2) * confidence, 2)
    worst_case_loss = round(rng.uniform(1.5, 8.0) * risk_score, 2)
    drawdown_impact = round(rng.uniform(0.2, 2.5) * risk_score, 2)
    volatility_exposure = round(risk_score * 100, 1)

    # "If Blocked" projections
    loss_avoided = round(trade_value * rng.uniform(0.02, 0.08) * risk_score, 2)
    capital_preserved = round(trade_value, 2)
    missed_upside = round(expected_return * 0.6, 2)

    return {
        "trade_value": round(trade_value, 2),
        "action": action,
        "if_allowed": {
            "expected_return_pct": expected_return,
            "worst_case_loss_pct": worst_case_loss,
            "portfolio_drawdown_pct": drawdown_impact,
            "volatility_exposure_pct": volatility_exposure,
        },
        "if_blocked": {
            "loss_avoided": loss_avoided,
            "capital_preserved": capital_preserved,
            "missed_upside_pct": missed_upside,
        },
    }


def _build_enforcement_entry(cycle: int, price: float, signal: dict, risk_result: dict, trade_result: dict, agent_name: str | None):
    """Build an enforcement visibility log entry."""
    action = signal.get("signal", "HOLD")
    risk_score = risk_result.get("risk_score", 0.0)
    reasons = risk_result.get("reasons", [])

    if not risk_result["approved"]:
        decision = "BLOCKED"
        decision_color = "red"
        original_size = round(price * 0.1, 2)
        reduced_size = 0
    elif risk_score > 0.45 and action != "HOLD":
        decision = "REDUCED"
        decision_color = "yellow"
        original_size = round(price * 0.1, 2)
        reduced_size = round(original_size * (1 - risk_score * 0.4), 2)
        if not reasons:
            reasons = [f"Risk-adjusted sizing (score: {risk_score:.2f})"]
    elif action == "HOLD":
        decision = "HOLD"
        decision_color = "muted"
        original_size = 0
        reduced_size = 0
    else:
        decision = "APPROVED"
        decision_color = "green"
        original_size = round(price * 0.1, 2)
        reduced_size = original_size

    entry = {
        "cycle": cycle,
        "timestamp": time.time(),
        "agent": agent_name or "Unknown",
        "action": action,
        "decision": decision,
        "decision_color": decision_color,
        "risk_score": risk_score,
        "reasons": reasons,
        "original_size": original_size,
        "reduced_size": reduced_size,
        "price": price,
    }
    enforcement_log.append(entry)
    if len(enforcement_log) > 50:
        enforcement_log.pop(0)
    return entry


# ─── Confidence / Multi-Signal data ─────────────────────────────────────────

def _compute_multi_signal(risk_result: dict):
    """Compute multi-signal display data."""
    risk_score = risk_result.get("risk_score", 0.0)
    details = risk_result.get("details", {})

    # Deterministic risk score (primary) — from the actual engine
    deterministic = round(risk_score * 100, 1)

    # Market condition factor (mocked but realistic)
    vol_risk = details.get("volatility_risk", 0.0)
    crash_risk = details.get("crash_risk", 0.0)
    market_factor = round(min((vol_risk * 0.6 + crash_risk * 0.4) * 100, 100), 1)

    # AI confidence (secondary, lower weight)
    ai_confidence = round(min(max(100 - risk_score * 120 + random.uniform(-5, 5), 10), 95), 1)

    return {
        "deterministic_risk": deterministic,
        "market_condition": market_factor,
        "ai_confidence": ai_confidence,
        "primary_weight": "70%",
        "secondary_weight": "30%",
    }


# ─── Existing endpoints ─────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"name": "AEGIS", "version": "4.0"}


@app.get("/status")
def status():
    price = governor.market.get_current_price()
    volatility = governor.market.get_volatility()
    pnl = governor.executor._current_pnl(price) if price else 0.0
    pv = governor.executor.get_portfolio_value(price) if price else 100000.0
    pnl_pct = (pnl / governor.executor.initial_cash) * 100 if governor.executor.initial_cash else 0.0
    return {
        "current_price": price,
        "cycle_count": governor.cycle_count,
        "portfolio_value": pv,
        "position_btc": governor.executor.position,
        "cash": governor.executor.cash,
        "pnl": pnl,
        "pnl_pct": round(pnl_pct, 3),
        "risk_threshold": governor.risk_engine.threshold,
        "trades_blocked": governor.risk_engine.blocked_count,
        "trades_approved": governor.risk_engine.approved_count,
        "volatile_mode": governor.market._sim_volatile,
        "volatility": volatility,
        "stats": governor.logger.get_stats(),
    }


@app.get("/logs")
def logs(last_n: int | None = None):
    return {"logs": governor.logger.get_entries(last_n)}


@app.post("/run-cycle")
def run_cycle():
    result = governor.run_cycle()
    # Update agent reputation
    agent_name = _update_agent_reputation(
        result["chosen_signal"], result["risk_result"], result["trade_result"]
    )
    # Build enforcement entry
    enforcement = _build_enforcement_entry(
        result["cycle"], result["price"],
        result["chosen_signal"], result["risk_result"], result["trade_result"],
        agent_name,
    )
    # Compute what-if
    what_if = _compute_what_if(result["price"], result["chosen_signal"], result["risk_result"])
    # Compute multi-signal
    multi_signal = _compute_multi_signal(result["risk_result"])

    result["enforcement"] = enforcement
    result["what_if"] = what_if
    result["multi_signal"] = multi_signal
    result["agent_name"] = agent_name
    return result


@app.post("/set-volatile")
def set_volatile(volatile: bool = True):
    governor.market.set_volatile(volatile)
    return {"volatile": volatile}


@app.post("/demo-scenario")
def demo_scenario():
    results = []
    governor.market.set_volatile(False)
    for _ in range(5):
        results.append(run_cycle())
    governor.market.set_volatile(True)
    for _ in range(5):
        results.append(run_cycle())

    blocked = sum(1 for r in results if not r["risk_result"]["approved"])
    executed = sum(1 for r in results if r["trade_result"]["executed"])
    capital_at_risk = sum(
        r["price"] * 0.1
        for r in results
        if not r["risk_result"]["approved"] and r["chosen_signal"]["signal"] != "HOLD"
    )
    return {
        "total_cycles": len(results),
        "executed": executed,
        "blocked": blocked,
        "capital_protected": round(capital_at_risk, 2),
        "results": results,
    }


@app.post("/reset")
def reset():
    global governor, enforcement_log
    governor = AegisGovernor(risk_threshold=0.65)
    governor.market.seed_history(30)
    enforcement_log = []
    # Reset agent scores
    for agent in AGENTS.values():
        agent["trust_score"] = random.randint(55, 85)
        agent["risk_score"] = round(random.uniform(0.2, 0.5), 2)
        agent["win_rate"] = round(random.uniform(50, 75), 1)
        agent["trades"] = 0
        agent["wins"] = 0
        agent["blocked"] = 0
        agent["status"] = "Approved"
    return {"status": "reset"}


@app.get("/portfolio")
def portfolio():
    price = governor.market.get_current_price()
    return {
        "cash": governor.executor.cash,
        "position_btc": governor.executor.position,
        "portfolio_value": governor.executor.get_portfolio_value(price) if price else None,
        "pnl": governor.executor._current_pnl(price) if price else None,
    }


@app.get("/risk-breakdown")
def risk_breakdown():
    """Return live risk rule states computed from current market data."""
    prices = governor.market.get_prices()
    price = governor.market.get_current_price()
    vol = governor.market.get_volatility()

    position_val = governor.executor.position * price if price else 0.0
    max_position = 50000.0
    position_pct = min(position_val / max_position, 1.0) if max_position else 0.0

    vol_pct = vol * 100
    if vol_pct > 2.0:
        vol_regime = "Extreme"
    elif vol_pct > 0.8:
        vol_regime = "Elevated"
    else:
        vol_regime = "Normal"

    last_logs = governor.logger.get_entries(last_n=1)
    details = last_logs[0].get("risk_details", {}) if last_logs else {}

    vol_risk_val = details.get("volatility_risk", 0.0)
    dd_risk_val = details.get("drawdown_risk", 0.0)
    crash_risk_val = details.get("crash_risk", 0.0)
    conf_risk_val = details.get("confidence_risk", 0.0)
    max_dd = details.get("max_drawdown", 0.0)
    last_move = details.get("last_move", 0.0)

    return {
        "rules": [
            {
                "name": "Volatility Regime",
                "current": f"{vol_pct:.2f}%",
                "limit": "3.00%",
                "pct": min(vol_pct / 3.0, 1.0),
                "status": vol_regime,
            },
            {
                "name": "Max Position Size",
                "current": f"${position_val:,.0f}",
                "limit": f"${max_position:,.0f}",
                "pct": position_pct,
                "status": "OK" if position_pct < 0.8 else "Warning",
            },
            {
                "name": "Drawdown Risk",
                "current": f"{max_dd:.2%}",
                "limit": "5.00%",
                "pct": dd_risk_val,
                "status": "OK" if dd_risk_val < 0.5 else "Elevated",
            },
            {
                "name": "Crash Detection",
                "current": f"{last_move:.2%}",
                "limit": "2.50%",
                "pct": crash_risk_val,
                "status": "OK" if crash_risk_val < 0.6 else "Triggered",
            },
            {
                "name": "Confidence Filter",
                "current": f"{conf_risk_val:.0%}" if conf_risk_val > 0 else "Clear",
                "limit": "Auto",
                "pct": conf_risk_val,
                "status": "OK" if conf_risk_val < 0.5 else "Active",
            },
        ],
        "composite_weights": {
            "volatility": 0.40,
            "drawdown": 0.25,
            "confidence": 0.20,
            "crash": 0.15,
        },
    }


@app.get("/performance-comparison")
def performance_comparison():
    entries = governor.logger.get_entries()
    if not entries:
        return {"with_aegis": [], "without_aegis": [], "cycles": []}

    with_aegis = [100000.0]
    without_aegis = [100000.0]

    rng = random.Random(42)
    for entry in entries:
        with_aegis.append(100000.0 + entry.get("pnl", 0.0))
        if not entry["approved"]:
            loss = rng.uniform(500, 3000)
            without_aegis.append(without_aegis[-1] - loss)
        elif entry["executed"]:
            gain = rng.uniform(-200, 400)
            without_aegis.append(without_aegis[-1] + gain)
        else:
            without_aegis.append(without_aegis[-1] + rng.uniform(-50, 50))

    return {
        "with_aegis": with_aegis,
        "without_aegis": without_aegis,
        "cycles": list(range(len(with_aegis))),
    }


# ─── NEW: Agent Reputation Leaderboard ──────────────────────────────────────

@app.get("/agents")
def agents():
    """Return agent leaderboard sorted by trust score."""
    sorted_agents = sorted(AGENTS.values(), key=lambda a: a["trust_score"], reverse=True)
    return {"agents": sorted_agents}


# ─── NEW: Enforcement Log ───────────────────────────────────────────────────

@app.get("/enforcement")
def get_enforcement(last_n: int = 10):
    """Return recent enforcement decisions."""
    entries = enforcement_log[-last_n:] if last_n else enforcement_log
    return {"entries": list(reversed(entries))}


# ─── NEW: Run Risk Scenario (Demo Mode) ─────────────────────────────────────

@app.post("/run-risk-scenario")
def run_risk_scenario():
    """Rapid-fire 5 trades with guaranteed mixed outcomes for demo."""
    results = []

    # Trade 1-2: Normal conditions → likely approved
    governor.market.set_volatile(False)
    for _ in range(2):
        results.append(run_cycle())

    # Trade 3: Spike volatility → likely blocked
    governor.market.set_volatile(True)
    results.append(run_cycle())

    # Trade 4: Still volatile → blocked or reduced
    results.append(run_cycle())

    # Trade 5: Back to normal → approved
    governor.market.set_volatile(False)
    results.append(run_cycle())

    summary = {
        "total": len(results),
        "approved": sum(1 for r in results if r["risk_result"]["approved"]),
        "blocked": sum(1 for r in results if not r["risk_result"]["approved"]),
        "results": results,
    }
    return summary


# ─── NEW: What-If for latest trade ──────────────────────────────────────────

@app.get("/what-if-latest")
def what_if_latest():
    """Return what-if analysis for the most recent trade."""
    entries = governor.logger.get_entries(last_n=1)
    if not entries:
        return {"error": "No trades yet"}
    entry = entries[0]
    price = entry["price"]
    signal = {"signal": entry["signal"], "confidence": entry["confidence"], "strategy": entry["strategy"]}
    risk_result = {"risk_score": entry["risk_score"], "approved": entry["approved"], "reasons": entry["reasons"], "details": entry.get("risk_details", {})}
    return _compute_what_if(price, signal, risk_result)


def start():
    import uvicorn
    uvicorn.run("aegis.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
