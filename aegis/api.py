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


def start():
    import uvicorn
    uvicorn.run("aegis.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
