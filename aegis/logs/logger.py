"""
AEGIS Logger — logs every cycle decision to JSON file and keeps in-memory history.
"""

import json
import time
import os
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trade_logs")
LOG_FILE = os.path.join(LOG_DIR, "aegis_log.json")


class AegisLogger:
    def __init__(self):
        self.entries: list[dict] = []
        os.makedirs(LOG_DIR, exist_ok=True)

    def log(self, cycle: int, price: float, signal: dict, risk_result: dict, trade_result: dict):
        entry = {
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "strategy": signal.get("strategy", "unknown"),
            "signal": signal.get("signal", "HOLD"),
            "confidence": signal.get("confidence", 0.0),
            "risk_score": risk_result.get("risk_score", 0.0),
            "approved": risk_result.get("approved", False),
            "reasons": risk_result.get("reasons", []),
            "risk_details": risk_result.get("details", {}),
            "executed": trade_result.get("executed", False),
            "pnl": trade_result.get("pnl", 0.0),
            "position": trade_result.get("position", 0.0),
            "cash": trade_result.get("cash", 0.0),
        }
        self.entries.append(entry)
        self._write_to_file()
        return entry

    def _write_to_file(self):
        try:
            with open(LOG_FILE, "w") as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write log file: {e}")

    def get_entries(self, last_n: int | None = None) -> list[dict]:
        if last_n:
            return self.entries[-last_n:]
        return list(self.entries)

    def get_stats(self) -> dict:
        if not self.entries:
            return {"total_cycles": 0, "blocked": 0, "executed": 0, "block_rate": 0.0}
        total = len(self.entries)
        blocked = sum(1 for e in self.entries if not e["approved"])
        executed = sum(1 for e in self.entries if e["executed"])
        return {
            "total_cycles": total,
            "blocked": blocked,
            "executed": executed,
            "holds": total - blocked - executed,
            "block_rate": round(blocked / total, 3) if total else 0.0,
            "avg_risk_score": round(sum(e["risk_score"] for e in self.entries) / total, 4),
        }
