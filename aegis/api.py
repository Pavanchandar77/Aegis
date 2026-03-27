"""
AEGIS FastAPI Backend

Endpoints:
  GET  /status     — current system state
  GET  /logs       — trade decision log
  POST /run-cycle  — trigger one trading cycle
  POST /start-demo — start the demo scenario
  GET  /portfolio  — portfolio summary
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.main import AegisGovernor

app = FastAPI(title="AEGIS Risk Governor", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

governor = AegisGovernor(risk_threshold=0.65)
governor.market.seed_history(30)


@app.get("/")
def root():
    return {"name": "AEGIS", "description": "Autonomous Risk Governor for Trading Agents", "status": "running"}


@app.get("/status")
def status():
    price = governor.market.get_current_price()
    return {
        "current_price": price,
        "cycle_count": governor.cycle_count,
        "portfolio_value": governor.executor.get_portfolio_value(price) if price else None,
        "position_btc": governor.executor.position,
        "cash": governor.executor.cash,
        "risk_threshold": governor.risk_engine.threshold,
        "trades_blocked": governor.risk_engine.blocked_count,
        "trades_approved": governor.risk_engine.approved_count,
        "volatile_mode": governor.market._sim_volatile,
        "stats": governor.logger.get_stats(),
    }


@app.get("/logs")
def logs(last_n: int | None = None):
    return {"logs": governor.logger.get_entries(last_n)}


@app.post("/run-cycle")
def run_cycle():
    result = governor.run_cycle()
    return result


@app.post("/set-volatile")
def set_volatile(volatile: bool = True):
    governor.market.set_volatile(volatile)
    return {"volatile": volatile, "message": f"Volatile mode {'ON' if volatile else 'OFF'}"}


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


def start():
    import uvicorn
    uvicorn.run("aegis.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
