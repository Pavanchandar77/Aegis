# AEGIS — Autonomous Risk Governor for Trading Agents

AI-driven trading system with a real-time risk engine that **blocks unsafe trades before execution**.

## Quick Start

```bash
pip install -r requirements.txt
```

### Terminal Demo
```bash
python run_demo.py
```

### API + Dashboard
```bash
# Terminal 1: Start API
python -m aegis.api

# Terminal 2: Start Dashboard
streamlit run aegis/dashboard.py
```

## Architecture

```
Market Data → Strategy Signals → Meta-Allocator → Risk Engine → Executor
                                                      ↓
                                              BLOCK or APPROVE
```

## Key Features

- **2 Trading Strategies**: Momentum + Mean Reversion
- **Meta-Agent Allocator**: Picks best strategy per cycle
- **Risk Engine**: Evaluates volatility, drawdown, crash risk → composite score
- **Trade Blocking**: Trades above risk threshold are BLOCKED
- **Full Logging**: Every decision recorded to JSON
- **Live Dashboard**: Streamlit UI with risk gauge and trade markers
