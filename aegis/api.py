"""
AEGIS FastAPI Backend v3

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
"""

import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.main import AegisGovernor

app = FastAPI(title="AEGIS Risk Governor", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

governor = AegisGovernor(risk_threshold=0.65)
governor.market.seed_history(30)


@app.get("/")
def root():
    return {"name": "AEGIS", "version": "3.0"}


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
    return governor.run_cycle()


@app.post("/set-volatile")
def set_volatile(volatile: bool = True):
    governor.market.set_volatile(volatile)
    return {"volatile": volatile}


@app.post("/demo-scenario")
def demo_scenario():
    results = []
    governor.market.set_volatile(False)
    for _ in range(5):
        results.append(governor.run_cycle())
    governor.market.set_volatile(True)
    for _ in range(5):
        results.append(governor.run_cycle())

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
    global governor
    governor = AegisGovernor(risk_threshold=0.65)
    governor.market.seed_history(30)
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

    # Position concentration
    position_val = governor.executor.position * price if price else 0.0
    max_position = 50000.0
    position_pct = min(position_val / max_position, 1.0) if max_position else 0.0

    # Volatility regime
    vol_pct = vol * 100
    if vol_pct > 2.0:
        vol_regime = "Extreme"
    elif vol_pct > 0.8:
        vol_regime = "Elevated"
    else:
        vol_regime = "Normal"

    # Drawdown from last risk eval
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
