"""
Market Data Provider — fetches BTC/USDT price (real via ccxt, falls back to simulation).
Maintains a rolling price history for strategy calculations.
"""

import time
import random
import numpy as np

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False


class MarketDataProvider:
    def __init__(self, symbol: str = "BTC/USDT", max_history: int = 100):
        self.symbol = symbol
        self.max_history = max_history
        self.prices: list[float] = []
        self.timestamps: list[float] = []
        self._exchange = None
        self._sim_price = 65000.0
        self._sim_volatile = False
        self._use_live = False  # Set True to attempt live data via ccxt

    def fetch_price(self) -> float:
        price = self._fetch_live() or self._simulate_price()
        self.prices.append(price)
        self.timestamps.append(time.time())
        if len(self.prices) > self.max_history:
            self.prices.pop(0)
            self.timestamps.pop(0)
        return price

    def _fetch_live(self) -> float | None:
        if not self._use_live or not HAS_CCXT:
            return None
        try:
            if not self._exchange:
                self._exchange = ccxt.binance({"enableRateLimit": True, "timeout": 5000})
            ticker = self._exchange.fetch_ticker(self.symbol)
            return float(ticker["last"])
        except Exception:
            return None

    def _simulate_price(self) -> float:
        if self._sim_volatile:
            # High volatility regime — big swings that trigger risk blocks
            change_pct = random.gauss(0, 0.06)
        else:
            # Normal market — small moves
            change_pct = random.gauss(0.0002, 0.004)

        self._sim_price *= (1 + change_pct)
        self._sim_price = max(self._sim_price, 10000)
        return round(self._sim_price, 2)

    def set_volatile(self, volatile: bool):
        """Toggle volatile market regime (for demo scenario)."""
        self._sim_volatile = volatile

    def get_prices(self) -> list[float]:
        return list(self.prices)

    def get_current_price(self) -> float | None:
        return self.prices[-1] if self.prices else None

    def get_sma(self, window: int = 20) -> float | None:
        if len(self.prices) < window:
            return None
        return float(np.mean(self.prices[-window:]))

    def get_volatility(self, window: int = 20) -> float:
        if len(self.prices) < 2:
            return 0.0
        recent = self.prices[-window:]
        returns = np.diff(recent) / np.array(recent[:-1])
        return float(np.std(returns))

    def seed_history(self, n: int = 30):
        """Seed with initial price history for strategies to work immediately."""
        for _ in range(n):
            self.fetch_price()
