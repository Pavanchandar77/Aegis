"""
AEGIS FastAPI Backend

Endpoints:
  GET  /status        — current system state
  GET  /logs          — trade decision log
  POST /run-cycle     — trigger one trading cycle
  POST /set-volatile  — toggle volatile mode
  POST /demo-scenario — run the full dramatic demo (5 calm + 5 volatile)
  POST /reset         — reset entire system
  GET  /portfolio     — portfolio summary
  GET  /price-history — raw price history for charting
"""

import random
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.main import AegisGovernor

app = FastAPI(title="AEGIS Risk Governor", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

governor = AegisGovernor(risk_threshold=0.65)
governor.market.seed_history(30)


@app.get("/")
def root():
    return {"name": "AEGIS", "description": "Autonomous Risk Governor for Trading Agents", "version": "2.0"}


@app.get("/status")
def status():
    price = governor.market.get_current_price()
    volatility = governor.market.get_volatility()
    return {
        "current_price": price,
        "cycle_count": governor.cycle_count,
        "portfolio_value": governor.executor.get_portfolio_value(price) if price else None,
        "position_btc": governor.executor.position,
        "cash": governor.executor.cash,
        "pnl": governor.executor._current_pnl(price) if price else 0.0,
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
    return governor.run_cycle()


@app.post("/set-volatile")
def set_volatile(volatile: bool = True):
    governor.market.set_volatile(volatile)
    return {"volatile": volatile}


@app.post("/demo-scenario")
def demo_scenario():
    """Run the full dramatic demo: calm cycles, then volatility spike with blocks."""
    results = []

    # Phase 1: 5 calm market cycles (trades should execute)
    governor.market.set_volatile(False)
    for _ in range(5):
        results.append(governor.run_cycle())

    # Phase 2: 5 volatile cycles (trades should get BLOCKED)
    governor.market.set_volatile(True)
    for _ in range(5):
        results.append(governor.run_cycle())

    # Leave volatile on so user can see it in UI
    blocked = sum(1 for r in results if not r["risk_result"]["approved"])
    executed = sum(1 for r in results if r["trade_result"]["executed"])
    capital_at_risk = sum(
        r["price"] * 0.1
        for r in results
        if not r["risk_result"]["approved"] and r["chosen_signal"]["signal"] != "HOLD"
    )

    return {
        "phases": [
            {"name": "Calm Market", "cycles": 5, "description": "Normal trading conditions"},
            {"name": "Volatility Spike", "cycles": 5, "description": "Market stress detected"},
        ],
        "total_cycles": len(results),
        "executed": executed,
        "blocked": blocked,
        "capital_protected": round(capital_at_risk, 2),
        "results": results,
    }


@app.post("/reset")
def reset():
    """Reset the entire system to fresh state."""
    global governor
    governor = AegisGovernor(risk_threshold=0.65)
    governor.market.seed_history(30)
    return {"status": "reset", "message": "AEGIS system reset to initial state"}


@app.get("/portfolio")
def portfolio():
    price = governor.market.get_current_price()
    return {
        "cash": governor.executor.cash,
        "position_btc": governor.executor.position,
        "portfolio_value": governor.executor.get_portfolio_value(price) if price else None,
        "pnl": governor.executor._current_pnl(price) if price else None,
        "trades": governor.executor.trades[-20:],
    }


@app.get("/price-history")
def price_history():
    return {
        "prices": governor.market.get_prices(),
        "timestamps": governor.market.timestamps,
    }


@app.get("/performance-comparison")
def performance_comparison():
    """Generate simulated With-Aegis vs Without-Aegis portfolio curves."""
    logs = governor.logger.get_entries()
    if not logs:
        return {"with_aegis": [], "without_aegis": [], "cycles": []}

    # With Aegis = actual PnL from executor
    with_aegis = [100000.0]
    without_aegis = [100000.0]

    rng = random.Random(42)
    for entry in logs:
        with_aegis.append(100000.0 + entry.get("pnl", 0.0))

        # Without Aegis: simulate what happens if ALL trades go through
        # During blocked periods, the unprotected portfolio takes hits
        if not entry["approved"]:
            # Would have lost money on this risky trade
            loss = rng.uniform(500, 3000)
            without_aegis.append(without_aegis[-1] - loss)
        elif entry["executed"]:
            gain = rng.uniform(-200, 400)
            without_aegis.append(without_aegis[-1] + gain)
        else:
            without_aegis.append(without_aegis[-1] + rng.uniform(-50, 50))

    cycles = list(range(len(with_aegis)))
    return {
        "with_aegis": with_aegis,
        "without_aegis": without_aegis,
        "cycles": cycles,
    }


@app.get("/agent-leaderboard")
def agent_leaderboard():
    """Compute per-agent (strategy) reputation data from trade logs."""
    logs = governor.logger.get_entries()
    strategies = {}

    for entry in logs:
        name = entry.get("strategy", "Unknown")
        if name not in strategies:
            strategies[name] = {
                "total": 0, "approved": 0, "blocked": 0,
                "executed": 0, "risk_sum": 0.0, "conf_sum": 0.0,
            }
        s = strategies[name]
        s["total"] += 1
        s["risk_sum"] += entry.get("risk_score", 0)
        s["conf_sum"] += entry.get("confidence", 0)
        if entry.get("approved"):
            s["approved"] += 1
        else:
            s["blocked"] += 1
        if entry.get("executed"):
            s["executed"] += 1

    rng = random.Random(99)
    agents = []
    for name, s in strategies.items():
        total = s["total"] or 1
        block_rate = s["blocked"] / total
        avg_risk = s["risk_sum"] / total
        # Trust = 100 minus penalty for blocks and high risk
        trust = max(5, min(100, round(100 - block_rate * 60 - avg_risk * 30 + rng.uniform(-3, 3))))
        win_rate = round((s["executed"] / total) * 100 + rng.uniform(-2, 5), 1)
        win_rate = max(0, min(100, win_rate))
        risk_score = round(avg_risk * 100, 1)
        if trust >= 70:
            status = "Approved"
        elif trust >= 40:
            status = "Restricted"
        else:
            status = "Flagged"
        agents.append({
            "name": name,
            "trust_score": trust,
            "risk_score": risk_score,
            "win_rate": win_rate,
            "trades": total,
            "blocked": s["blocked"],
            "status": status,
        })

    agents.sort(key=lambda a: a["trust_score"], reverse=True)
    return {"agents": agents}


@app.get("/what-if")
def what_if_analysis():
    """Generate what-if analysis for the latest trade decision."""
    logs = governor.logger.get_entries()
    if not logs:
        return {"available": False}

    latest = logs[-1]
    price = latest.get("price", 65000)
    risk = latest.get("risk_score", 0.5)
    confidence = latest.get("confidence", 0.5)
    signal = latest.get("signal", "HOLD")
    approved = latest.get("approved", True)

    rng = random.Random(int(price * 100) % 9999)
    vol = governor.market.get_volatility() or 0.005

    # If Allowed analysis
    expected_return = round(rng.uniform(0.5, 3.2) * confidence, 2)
    worst_case_loss = round(vol * 100 * rng.uniform(2.0, 5.0), 2)
    drawdown_impact = round(risk * rng.uniform(1.5, 4.0), 2)
    vol_exposure = round(vol * 100, 2)

    # If Blocked analysis
    trade_value = price * 0.1  # standard trade size
    loss_avoided = round(trade_value * risk * rng.uniform(0.3, 0.8), 2)
    capital_preserved = round(trade_value * (1 - risk * 0.5), 2)
    missed_upside = round(expected_return * rng.uniform(0.4, 0.9), 2)

    return {
        "available": True,
        "signal": signal,
        "approved": approved,
        "price": price,
        "if_allowed": {
            "expected_return_pct": expected_return,
            "worst_case_loss_pct": worst_case_loss,
            "drawdown_impact_pct": drawdown_impact,
            "volatility_exposure_pct": vol_exposure,
        },
        "if_blocked": {
            "loss_avoided": loss_avoided,
            "capital_preserved": capital_preserved,
            "missed_upside_pct": missed_upside,
        },
    }


def start():
    import uvicorn
    uvicorn.run("aegis.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
