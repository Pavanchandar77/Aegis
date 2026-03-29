"""
AEGIS — Vercel Serverless FastAPI Backend
All modules inlined for Vercel compatibility.
"""

import random
import time
import math
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════════
# INLINED MODULES (Vercel serverless can't do relative imports)
# ═══════════════════════════════════════════════════════════════

# ── Market Data Provider ──
class MarketDataProvider:
    def __init__(self, symbol="BTC/USDT", max_history=100):
        self.symbol = symbol
        self.max_history = max_history
        self.prices: list[float] = []
        self.timestamps: list[float] = []
        self._sim_price = 65000.0
        self._sim_volatile = False

    def fetch_price(self) -> float:
        price = self._simulate_price()
        self.prices.append(price)
        self.timestamps.append(time.time())
        if len(self.prices) > self.max_history:
            self.prices.pop(0)
            self.timestamps.pop(0)
        return price

    def _simulate_price(self) -> float:
        if self._sim_volatile:
            change_pct = random.gauss(0, 0.06)
        else:
            change_pct = random.gauss(0.0002, 0.004)
        self._sim_price *= (1 + change_pct)
        self._sim_price = max(self._sim_price, 10000)
        return round(self._sim_price, 2)

    def set_volatile(self, volatile: bool):
        self._sim_volatile = volatile

    def get_prices(self) -> list[float]:
        return list(self.prices)

    def get_current_price(self):
        return self.prices[-1] if self.prices else None

    def get_sma(self, window=20):
        if len(self.prices) < window:
            return None
        return sum(self.prices[-window:]) / window

    def get_volatility(self, window=20) -> float:
        if len(self.prices) < 2:
            return 0.0
        recent = self.prices[-window:]
        returns = []
        for i in range(1, len(recent)):
            returns.append((recent[i] - recent[i-1]) / recent[i-1])
        if not returns:
            return 0.0
        mean_r = sum(returns) / len(returns)
        variance = sum((r - mean_r) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)

    def seed_history(self, n=30):
        for _ in range(n):
            self.fetch_price()


# ── Momentum Strategy ──
class MomentumStrategy:
    name = "Momentum"

    def generate_signal(self, prices):
        if len(prices) < 5:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}
        short_avg = sum(prices[-3:]) / 3
        medium_avg = sum(prices[-10:]) / min(len(prices), 10)
        momentum = (short_avg - medium_avg) / medium_avg
        if momentum > 0.005:
            signal = "BUY"
            confidence = min(abs(momentum) * 20, 1.0)
        elif momentum < -0.005:
            signal = "SELL"
            confidence = min(abs(momentum) * 20, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.2
        return {"signal": signal, "confidence": round(confidence, 3), "strategy": self.name, "momentum": round(momentum, 6)}


# ── Mean Reversion Strategy ──
class MeanReversionStrategy:
    name = "MeanReversion"

    def __init__(self, window=20):
        self.window = window

    def generate_signal(self, prices):
        if len(prices) < self.window:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}
        recent = prices[-self.window:]
        sma = sum(recent) / len(recent)
        mean_r = sum(recent) / len(recent)
        variance = sum((p - mean_r) ** 2 for p in recent) / len(recent)
        std = math.sqrt(variance)
        current = prices[-1]
        if std == 0:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}
        z_score = (current - sma) / std
        if z_score > 1.0:
            signal = "SELL"
            confidence = min(abs(z_score) / 3.0, 1.0)
        elif z_score < -1.0:
            signal = "BUY"
            confidence = min(abs(z_score) / 3.0, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.1
        return {"signal": signal, "confidence": round(confidence, 3), "strategy": self.name, "z_score": round(z_score, 4)}


# ── Risk Engine ──
class RiskEngine:
    def __init__(self, threshold=0.65):
        self.threshold = threshold
        self.blocked_count = 0
        self.approved_count = 0

    def evaluate(self, prices, signal):
        if len(prices) < 5:
            return {"approved": True, "risk_score": 0.0, "reasons": [], "details": {}}

        reasons = []
        details = {}

        # Volatility Risk
        returns = []
        for i in range(max(0, len(prices)-30), len(prices)-1):
            if i+1 < len(prices):
                returns.append((prices[i+1] - prices[i]) / prices[i])
        if returns:
            mean_r = sum(returns) / len(returns)
            vol = math.sqrt(sum((r - mean_r)**2 for r in returns) / len(returns))
        else:
            vol = 0.0
        vol_risk = min(vol / 0.03, 1.0)
        details["volatility"] = round(vol, 6)
        details["volatility_risk"] = round(vol_risk, 3)
        if vol_risk > 0.6:
            reasons.append(f"High volatility ({vol:.4%})")

        # Drawdown Risk
        window = prices[-30:]
        peak = window[0]
        max_dd = 0.0
        for p in window:
            peak = max(peak, p)
            dd = (peak - p) / peak
            max_dd = max(max_dd, dd)
        dd_risk = min(max_dd / 0.05, 1.0)
        details["max_drawdown"] = round(max_dd, 6)
        details["drawdown_risk"] = round(dd_risk, 3)
        if dd_risk > 0.5:
            reasons.append(f"Significant drawdown ({max_dd:.2%})")

        # Confidence Risk
        confidence = signal.get("confidence", 0.5)
        conf_risk = 0.0
        if confidence > 0.8 and vol_risk > 0.5:
            conf_risk = 0.7
            reasons.append("High confidence in volatile market")
        details["confidence_risk"] = round(conf_risk, 3)

        # Crash Risk
        if len(prices) >= 3:
            last_move = abs(prices[-1] - prices[-2]) / prices[-2]
            crash_risk = min(last_move / 0.025, 1.0)
            details["last_move"] = round(last_move, 6)
            details["crash_risk"] = round(crash_risk, 3)
            if crash_risk > 0.6:
                reasons.append(f"Sudden price move ({last_move:.2%})")
        else:
            crash_risk = 0.0
            details["crash_risk"] = 0.0

        risk_score = 0.40 * vol_risk + 0.25 * dd_risk + 0.20 * conf_risk + 0.15 * crash_risk
        risk_score = round(min(risk_score, 1.0), 4)
        approved = risk_score <= self.threshold

        if approved:
            self.approved_count += 1
        else:
            self.blocked_count += 1
            if not reasons:
                reasons.append("Composite risk above threshold")

        return {"approved": approved, "risk_score": risk_score, "threshold": self.threshold, "reasons": reasons, "details": details}


# ── Allocator ──
class Allocator:
    def __init__(self):
        self.performance = {}

    def select_strategy(self, signals):
        actionable = [s for s in signals if s["signal"] != "HOLD"]
        if not actionable:
            actionable = signals
        return max(actionable, key=lambda s: s.get("confidence", 0.0))


# ── Trade Executor ──
class TradeExecutor:
    def __init__(self):
        self.position = 0.0
        self.cash = 100_000.0
        self.initial_cash = 100_000.0
        self.trades = []
        self.trade_size = 0.1

    def execute(self, signal, risk_result, price):
        action = signal["signal"]
        strategy = signal.get("strategy", "unknown")

        if not risk_result["approved"]:
            result = {"executed": False, "action": action, "strategy": strategy, "price": price,
                      "reason": "; ".join(risk_result["reasons"]), "risk_score": risk_result["risk_score"],
                      "timestamp": time.time(), "pnl": self._current_pnl(price)}
            self.trades.append(result)
            return result

        if action == "BUY" and self.cash >= price * self.trade_size:
            self.position += self.trade_size
            self.cash -= price * self.trade_size
        elif action == "SELL" and self.position >= self.trade_size:
            self.position -= self.trade_size
            self.cash += price * self.trade_size
        elif action == "HOLD":
            result = {"executed": True, "action": "HOLD", "strategy": strategy, "price": price,
                      "reason": "No action needed", "risk_score": risk_result["risk_score"],
                      "timestamp": time.time(), "pnl": self._current_pnl(price)}
            self.trades.append(result)
            return result
        else:
            result = {"executed": False, "action": action, "strategy": strategy, "price": price,
                      "reason": "Insufficient funds/position", "risk_score": risk_result["risk_score"],
                      "timestamp": time.time(), "pnl": self._current_pnl(price)}
            self.trades.append(result)
            return result

        result = {"executed": True, "action": action, "strategy": strategy, "price": price,
                  "reason": "Approved", "risk_score": risk_result["risk_score"],
                  "timestamp": time.time(), "position": self.position, "cash": round(self.cash, 2),
                  "pnl": self._current_pnl(price)}
        self.trades.append(result)
        return result

    def _current_pnl(self, price):
        return round(self.cash + self.position * price - self.initial_cash, 2)

    def get_portfolio_value(self, price):
        return round(self.cash + self.position * price, 2)


# ── Logger (in-memory only for serverless) ──
class AegisLogger:
    def __init__(self):
        self.entries = []

    def log(self, cycle, price, signal, risk_result, trade_result):
        entry = {
            "cycle": cycle, "timestamp": datetime.now().isoformat(), "price": price,
            "strategy": signal.get("strategy", "unknown"), "signal": signal.get("signal", "HOLD"),
            "confidence": signal.get("confidence", 0.0), "risk_score": risk_result.get("risk_score", 0.0),
            "approved": risk_result.get("approved", False), "reasons": risk_result.get("reasons", []),
            "executed": trade_result.get("executed", False), "pnl": trade_result.get("pnl", 0.0),
        }
        self.entries.append(entry)
        return entry

    def get_entries(self, last_n=None):
        if last_n:
            return self.entries[-last_n:]
        return list(self.entries)

    def get_stats(self):
        if not self.entries:
            return {"total_cycles": 0, "blocked": 0, "executed": 0, "block_rate": 0.0}
        total = len(self.entries)
        blocked = sum(1 for e in self.entries if not e["approved"])
        executed = sum(1 for e in self.entries if e["executed"])
        return {
            "total_cycles": total, "blocked": blocked, "executed": executed,
            "holds": total - blocked - executed,
            "block_rate": round(blocked / total, 3) if total else 0.0,
            "avg_risk_score": round(sum(e["risk_score"] for e in self.entries) / total, 4),
        }


# ═══════════════════════════════════════════════════════════════
# AEGIS GOVERNOR
# ═══════════════════════════════════════════════════════════════

class AegisGovernor:
    def __init__(self, risk_threshold=0.65):
        self.market = MarketDataProvider()
        self.strategies = [MomentumStrategy(), MeanReversionStrategy()]
        self.risk_engine = RiskEngine(threshold=risk_threshold)
        self.allocator = Allocator()
        self.executor = TradeExecutor()
        self.logger = AegisLogger()
        self.cycle_count = 0

    def run_cycle(self):
        self.cycle_count += 1
        price = self.market.fetch_price()
        prices = self.market.get_prices()
        signals = [s.generate_signal(prices) for s in self.strategies]
        chosen = self.allocator.select_strategy(signals)
        risk_result = self.risk_engine.evaluate(prices, chosen)
        trade_result = self.executor.execute(chosen, risk_result, price)
        self.logger.log(self.cycle_count, price, chosen, risk_result, trade_result)
        return {
            "cycle": self.cycle_count, "price": price, "all_signals": signals,
            "chosen_signal": chosen, "risk_result": risk_result,
            "trade_result": trade_result,
            "portfolio_value": self.executor.get_portfolio_value(price),
        }


# ═══════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════

app = FastAPI(title="AEGIS Risk Governor", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

governor = AegisGovernor(risk_threshold=0.65)
governor.market.seed_history(30)


@app.get("/api")
def root():
    return {"name": "AEGIS", "description": "Autonomous Risk Governor for Trading Agents", "version": "2.0"}


@app.get("/api/status")
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


@app.get("/api/logs")
def logs(last_n: int = None):
    return {"logs": governor.logger.get_entries(last_n)}


@app.post("/api/run-cycle")
def run_cycle():
    return governor.run_cycle()


@app.post("/api/set-volatile")
def set_volatile(volatile: bool = True):
    governor.market.set_volatile(volatile)
    return {"volatile": volatile}


@app.post("/api/demo-scenario")
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
        "phases": [
            {"name": "Calm Market", "cycles": 5, "description": "Normal trading conditions"},
            {"name": "Volatility Spike", "cycles": 5, "description": "Market stress detected"},
        ],
        "total_cycles": len(results), "executed": executed, "blocked": blocked,
        "capital_protected": round(capital_at_risk, 2), "results": results,
    }


@app.post("/api/reset")
def reset():
    global governor
    governor = AegisGovernor(risk_threshold=0.65)
    governor.market.seed_history(30)
    return {"status": "reset", "message": "AEGIS system reset to initial state"}


@app.get("/api/portfolio")
def portfolio():
    price = governor.market.get_current_price()
    return {
        "cash": governor.executor.cash,
        "position_btc": governor.executor.position,
        "portfolio_value": governor.executor.get_portfolio_value(price) if price else None,
        "pnl": governor.executor._current_pnl(price) if price else None,
        "trades": governor.executor.trades[-20:],
    }


@app.get("/api/price-history")
def price_history():
    return {"prices": governor.market.get_prices(), "timestamps": governor.market.timestamps}


@app.get("/api/performance-comparison")
def performance_comparison():
    logs_data = governor.logger.get_entries()
    if not logs_data:
        return {"with_aegis": [], "without_aegis": [], "cycles": []}

    with_aegis = [100000.0]
    without_aegis = [100000.0]
    rng = random.Random(42)
    for entry in logs_data:
        with_aegis.append(100000.0 + entry.get("pnl", 0.0))
        if not entry["approved"]:
            loss = rng.uniform(500, 3000)
            without_aegis.append(without_aegis[-1] - loss)
        elif entry["executed"]:
            gain = rng.uniform(-200, 400)
            without_aegis.append(without_aegis[-1] + gain)
        else:
            without_aegis.append(without_aegis[-1] + rng.uniform(-50, 50))

    cycles = list(range(len(with_aegis)))
    return {"with_aegis": with_aegis, "without_aegis": without_aegis, "cycles": cycles}


@app.get("/api/agent-leaderboard")
def agent_leaderboard():
    logs_data = governor.logger.get_entries()
    strategies = {}
    for entry in logs_data:
        name = entry.get("strategy", "Unknown")
        if name not in strategies:
            strategies[name] = {"total": 0, "approved": 0, "blocked": 0, "executed": 0, "risk_sum": 0.0, "conf_sum": 0.0}
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
        trust = max(5, min(100, round(100 - block_rate * 60 - avg_risk * 30 + rng.uniform(-3, 3))))
        win_rate = round((s["executed"] / total) * 100 + rng.uniform(-2, 5), 1)
        win_rate = max(0, min(100, win_rate))
        risk_score = round(avg_risk * 100, 1)
        if trust >= 70:
            st = "Approved"
        elif trust >= 40:
            st = "Restricted"
        else:
            st = "Flagged"
        agents.append({"name": name, "trust_score": trust, "risk_score": risk_score,
                       "win_rate": win_rate, "trades": total, "blocked": s["blocked"], "status": st})

    agents.sort(key=lambda a: a["trust_score"], reverse=True)
    return {"agents": agents}


@app.get("/api/what-if")
def what_if_analysis():
    logs_data = governor.logger.get_entries()
    if not logs_data:
        return {"available": False}

    latest = logs_data[-1]
    price = latest.get("price", 65000)
    risk = latest.get("risk_score", 0.5)
    confidence = latest.get("confidence", 0.5)
    signal = latest.get("signal", "HOLD")
    approved = latest.get("approved", True)

    rng = random.Random(int(price * 100) % 9999)
    vol = governor.market.get_volatility() or 0.005

    expected_return = round(rng.uniform(0.5, 3.2) * confidence, 2)
    worst_case_loss = round(vol * 100 * rng.uniform(2.0, 5.0), 2)
    drawdown_impact = round(risk * rng.uniform(1.5, 4.0), 2)
    vol_exposure = round(vol * 100, 2)

    trade_value = price * 0.1
    loss_avoided = round(trade_value * risk * rng.uniform(0.3, 0.8), 2)
    capital_preserved = round(trade_value * (1 - risk * 0.5), 2)
    missed_upside = round(expected_return * rng.uniform(0.4, 0.9), 2)

    return {
        "available": True, "signal": signal, "approved": approved, "price": price,
        "if_allowed": {
            "expected_return_pct": expected_return, "worst_case_loss_pct": worst_case_loss,
            "drawdown_impact_pct": drawdown_impact, "volatility_exposure_pct": vol_exposure,
        },
        "if_blocked": {
            "loss_avoided": loss_avoided, "capital_preserved": capital_preserved,
            "missed_upside_pct": missed_upside,
        },
    }
