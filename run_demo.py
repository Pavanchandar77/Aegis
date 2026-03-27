#!/usr/bin/env python3
"""Quick launcher for AEGIS terminal demo."""

from aegis.main import AegisGovernor

if __name__ == "__main__":
    governor = AegisGovernor(risk_threshold=0.65)
    governor.run_demo(cycles=30, delay=0.8)
