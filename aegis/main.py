"""
AEGIS — Autonomous Risk Governor for Trading Agents

Main orchestration loop. Runs trading cycles:
  1. Fetch price
  2. Generate signals from all strategies
  3. Allocator picks best strategy
  4. Risk engine evaluates
  5. Executor acts (or blocks)
  6. Logger records everything
"""

import time
import sys

from aegis.data.market_data import MarketDataProvider
from aegis.strategies.momentum import MomentumStrategy
from aegis.strategies.mean_reversion import MeanReversionStrategy
from aegis.core.risk_engine import RiskEngine
from aegis.core.allocator import Allocator
from aegis.core.executor import TradeExecutor
from aegis.logs.logger import AegisLogger


class AegisGovernor:
    def __init__(self, risk_threshold: float = 0.65):
        self.market = MarketDataProvider()
        self.strategies = [MomentumStrategy(), MeanReversionStrategy()]
        self.risk_engine = RiskEngine(threshold=risk_threshold)
        self.allocator = Allocator()
        self.executor = TradeExecutor()
        self.logger = AegisLogger()
        self.cycle_count = 0

    def run_cycle(self) -> dict:
        self.cycle_count += 1
        price = self.market.fetch_price()
        prices = self.market.get_prices()

        # Generate signals from all strategies
        signals = [s.generate_signal(prices) for s in self.strategies]

        # Meta-agent picks best
        chosen = self.allocator.select_strategy(signals)

        # Risk engine evaluates
        risk_result = self.risk_engine.evaluate(prices, chosen)

        # Execute or block
        trade_result = self.executor.execute(chosen, risk_result, price)

        # Log everything
        entry = self.logger.log(self.cycle_count, price, chosen, risk_result, trade_result)

        return {
            "cycle": self.cycle_count,
            "price": price,
            "all_signals": signals,
            "chosen_signal": chosen,
            "risk_result": risk_result,
            "trade_result": trade_result,
            "portfolio_value": self.executor.get_portfolio_value(price),
        }

    def run_demo(self, cycles: int = 30, delay: float = 1.0):
        """Run the full demo scenario with volatility spike."""
        print("=" * 70)
        print("  🛡️  AEGIS — Autonomous Risk Governor for Trading Agents")
        print("=" * 70)
        print(f"\n  Risk Threshold: {self.risk_engine.threshold}")
        print(f"  Strategies: {[s.name for s in self.strategies]}")
        print(f"  Starting Capital: ${self.executor.cash:,.2f}")
        print()

        # Seed some price history
        print("  Seeding market data...")
        self.market.seed_history(30)
        print(f"  Initial price: ${self.market.get_current_price():,.2f}")
        print("-" * 70)

        for i in range(cycles):
            # Activate volatile regime mid-demo
            if i == cycles // 3:
                print("\n" + "!" * 70)
                print("  ⚠️  MARKET VOLATILITY SPIKE DETECTED!")
                print("!" * 70)
                self.market.set_volatile(True)

            # Return to calm near end
            if i == 2 * cycles // 3:
                print("\n" + "-" * 70)
                print("  📉 Market calming down...")
                print("-" * 70)
                self.market.set_volatile(False)

            print(f"\n{'─' * 50} Cycle {i + 1}/{cycles}")
            result = self.run_cycle()
            time.sleep(delay)

        # Summary
        stats = self.logger.get_stats()
        print("\n" + "=" * 70)
        print("  📊 AEGIS SESSION SUMMARY")
        print("=" * 70)
        print(f"  Total Cycles:     {stats['total_cycles']}")
        print(f"  Trades Executed:  {stats['executed']}")
        print(f"  Trades BLOCKED:   {stats['blocked']}")
        print(f"  Block Rate:       {stats['block_rate']:.1%}")
        print(f"  Avg Risk Score:   {stats['avg_risk_score']:.4f}")
        final_price = self.market.get_current_price()
        print(f"  Final Portfolio:  ${self.executor.get_portfolio_value(final_price):,.2f}")
        print(f"  P&L:             ${self.executor._current_pnl(final_price):,.2f}")
        print("=" * 70)


def main():
    governor = AegisGovernor(risk_threshold=0.65)
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
    governor.run_demo(cycles=cycles, delay=delay)


if __name__ == "__main__":
    main()
