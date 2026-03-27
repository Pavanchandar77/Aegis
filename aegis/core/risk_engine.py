"""
AEGIS Risk Engine — the CORE of the system.

Evaluates every trade signal before execution.
Computes a composite risk score (0–1) and BLOCKS trades above threshold.

Risk factors:
  1. Volatility risk — std deviation of recent returns
  2. Drawdown risk — max drawdown in recent window
  3. Position concentration risk — based on signal confidence extremes
  4. Momentum crash risk — sudden large moves
"""

import numpy as np


class RiskEngine:
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold
        self.blocked_count = 0
        self.approved_count = 0

    def evaluate(self, prices: list[float], signal: dict) -> dict:
        if len(prices) < 5:
            return {
                "approved": True,
                "risk_score": 0.0,
                "reasons": [],
                "details": {},
            }

        reasons = []
        details = {}

        # --- 1. Volatility Risk ---
        returns = np.diff(prices[-30:]) / np.array(prices[-30:])[:-1]
        vol = float(np.std(returns))
        vol_risk = min(vol / 0.03, 1.0)  # normalize: 3% std = max risk
        details["volatility"] = round(vol, 6)
        details["volatility_risk"] = round(vol_risk, 3)
        if vol_risk > 0.6:
            reasons.append(f"High volatility ({vol:.4%})")

        # --- 2. Drawdown Risk ---
        window = prices[-30:]
        peak = window[0]
        max_dd = 0.0
        for p in window:
            peak = max(peak, p)
            dd = (peak - p) / peak
            max_dd = max(max_dd, dd)
        dd_risk = min(max_dd / 0.05, 1.0)  # 5% drawdown = max risk
        details["max_drawdown"] = round(max_dd, 6)
        details["drawdown_risk"] = round(dd_risk, 3)
        if dd_risk > 0.5:
            reasons.append(f"Significant drawdown ({max_dd:.2%})")

        # --- 3. Position Size / Confidence Risk ---
        confidence = signal.get("confidence", 0.5)
        # Very high confidence in volatile markets is dangerous
        conf_risk = 0.0
        if confidence > 0.8 and vol_risk > 0.5:
            conf_risk = 0.7
            reasons.append("High confidence in volatile market")
        details["confidence_risk"] = round(conf_risk, 3)

        # --- 4. Momentum Crash Risk ---
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

        # --- Composite Risk Score (weighted) ---
        risk_score = (
            0.40 * vol_risk
            + 0.25 * dd_risk
            + 0.20 * conf_risk
            + 0.15 * crash_risk
        )
        risk_score = round(min(risk_score, 1.0), 4)

        approved = risk_score <= self.threshold

        if approved:
            self.approved_count += 1
        else:
            self.blocked_count += 1
            if not reasons:
                reasons.append("Composite risk above threshold")

        return {
            "approved": approved,
            "risk_score": risk_score,
            "threshold": self.threshold,
            "reasons": reasons,
            "details": details,
        }
