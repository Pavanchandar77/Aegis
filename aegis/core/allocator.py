"""
Capital Allocator — meta-agent that picks the best strategy each cycle.

Selection based on:
  - Signal confidence
  - Recent strategy performance (tracked internally)
"""


class Allocator:
    def __init__(self):
        self.performance: dict[str, list[float]] = {}

    def select_strategy(self, signals: list[dict]) -> dict:
        actionable = [s for s in signals if s["signal"] != "HOLD"]
        if not actionable:
            actionable = signals

        best = max(actionable, key=lambda s: self._score(s))
        return best

    def _score(self, signal: dict) -> float:
        confidence = signal.get("confidence", 0.0)
        name = signal.get("strategy", "")
        perf_bonus = 0.0
        if name in self.performance and self.performance[name]:
            recent = self.performance[name][-10:]
            perf_bonus = sum(recent) / len(recent) * 0.3
        return confidence + perf_bonus

    def record_result(self, strategy_name: str, profit: float):
        if strategy_name not in self.performance:
            self.performance[strategy_name] = []
        self.performance[strategy_name].append(profit)
