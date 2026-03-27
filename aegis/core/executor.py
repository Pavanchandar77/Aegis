"""
Trade Executor — simulates trade execution.
Only executes if the risk engine approves. Clearly logs blocked trades.
"""

import time


class TradeExecutor:
    def __init__(self):
        self.position: float = 0.0
        self.cash: float = 100_000.0
        self.initial_cash: float = 100_000.0
        self.trades: list[dict] = []
        self.trade_size = 0.1  # BTC per trade

    def execute(self, signal: dict, risk_result: dict, price: float) -> dict:
        action = signal["signal"]
        strategy = signal.get("strategy", "unknown")

        if not risk_result["approved"]:
            result = {
                "executed": False,
                "action": action,
                "strategy": strategy,
                "price": price,
                "reason": "; ".join(risk_result["reasons"]),
                "risk_score": risk_result["risk_score"],
                "timestamp": time.time(),
                "pnl": self._current_pnl(price),
            }
            print(f"\n  ❌ TRADE BLOCKED | {strategy} wanted {action} @ ${price:,.2f}")
            print(f"     Risk Score: {risk_result['risk_score']:.4f} > threshold {risk_result['threshold']}")
            print(f"     Reasons: {'; '.join(risk_result['reasons'])}")
            self.trades.append(result)
            return result

        # Execute the trade
        if action == "BUY" and self.cash >= price * self.trade_size:
            cost = price * self.trade_size
            self.position += self.trade_size
            self.cash -= cost
        elif action == "SELL" and self.position >= self.trade_size:
            revenue = price * self.trade_size
            self.position -= self.trade_size
            self.cash += revenue
        elif action == "HOLD":
            result = {
                "executed": True,
                "action": "HOLD",
                "strategy": strategy,
                "price": price,
                "reason": "No action needed",
                "risk_score": risk_result["risk_score"],
                "timestamp": time.time(),
                "pnl": self._current_pnl(price),
            }
            print(f"\n  ⏸  HOLD | {strategy} @ ${price:,.2f}")
            self.trades.append(result)
            return result
        else:
            result = {
                "executed": False,
                "action": action,
                "strategy": strategy,
                "price": price,
                "reason": "Insufficient funds/position",
                "risk_score": risk_result["risk_score"],
                "timestamp": time.time(),
                "pnl": self._current_pnl(price),
            }
            self.trades.append(result)
            return result

        result = {
            "executed": True,
            "action": action,
            "strategy": strategy,
            "price": price,
            "reason": "Approved",
            "risk_score": risk_result["risk_score"],
            "timestamp": time.time(),
            "position": self.position,
            "cash": round(self.cash, 2),
            "pnl": self._current_pnl(price),
        }
        print(f"\n  ✅ TRADE EXECUTED | {action} via {strategy} @ ${price:,.2f}")
        print(f"     Risk Score: {risk_result['risk_score']:.4f}")
        print(f"     Position: {self.position:.4f} BTC | Cash: ${self.cash:,.2f}")
        self.trades.append(result)
        return result

    def _current_pnl(self, price: float) -> float:
        portfolio_value = self.cash + self.position * price
        return round(portfolio_value - self.initial_cash, 2)

    def get_portfolio_value(self, price: float) -> float:
        return round(self.cash + self.position * price, 2)
