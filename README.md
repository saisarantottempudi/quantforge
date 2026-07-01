# QuantForge

[![CI](https://github.com/saisarantottempudi/quantforge/actions/workflows/ci.yml/badge.svg)](https://github.com/saisarantottempudi/quantforge/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

**Language-agnostic backtesting and paper trading engine.** Write your strategy in any language — Python, Go, TypeScript, Rust, anything with WebSocket support. QuantForge handles data, simulation, portfolio tracking, and observability.

## How it works

1. Create a session (REST POST) — choose symbols, date range, capital, and data adapter
2. Connect via WebSocket — receive `BAR` events as price data streams
3. Send `ORDER` events back — the engine fills at bar close with configurable slippage and fees
4. Fetch the report (REST GET) — Sharpe ratio, max drawdown, VaR, equity curve

## Quickstart

**Requires Docker.**

```bash
git clone https://github.com/saisarantottempudi/quantforge.git
cd quantforge
docker compose up --build
```

Then run any example client:

```bash
# Python
cd examples/python && pip install -r requirements.txt && python sma_crossover.py

# Go
cd examples/go && go mod tidy && go run .

# TypeScript
cd examples/typescript && npm install && npm start
```

## Supported assets

| Adapter | Asset class | API key? |
|---------|-------------|----------|
| `yfinance` | Equities, ETFs | No |
| `ccxt` | Crypto (100+ exchanges) | No (public data) |
| `forex` | Forex pairs | Optional (Alpha Vantage free tier) |
| `synthetic` | Synthetic / testing | No |

## REST API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/sessions` | Create session |
| `GET` | `/sessions/{id}` | Session status |
| `GET` | `/sessions/{id}/report` | Performance report |
| `GET` | `/sessions/{id}/trades` | Trade history |
| `GET` | `/sessions/{id}/portfolio` | Current portfolio |
| `DELETE` | `/sessions/{id}` | Delete session |
| `WS` | `/sessions/{id}/stream` | Bar/fill/portfolio stream |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/health` | Health check |

Interactive docs at http://localhost:8000/docs

## Session config

```json
{
  "symbols": ["AAPL", "MSFT"],
  "start": "2023-01-01",
  "end": "2023-12-31",
  "capital": 10000.0,
  "data_adapter": "yfinance",
  "slippage": {"model": "fixed_bps", "value": 5},
  "fees": {"model": "percent", "value": 0.001},
  "portfolio_tick_interval": 10
}
```

## Docker

**Engine only:**
```bash
docker compose up --build
```

**Engine + Prometheus + Grafana:**
```bash
docker compose -f docker-compose.observability.yml up --build
```

- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Examples

| Language | File | Dependencies |
|----------|------|--------------|
| Python | `examples/python/sma_crossover.py` | `httpx`, `websockets` |
| Go | `examples/go/main.go` | `nhooyr.io/websocket` |
| TypeScript | `examples/typescript/sma_crossover.ts` | `ws`, `ts-node` |

All examples implement SMA(10/20) crossover on AAPL 2023 data.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v          # 41 tests
ruff check quantforge/ tests/
bandit -r quantforge/ -ll
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## License

Apache-2.0 — see [LICENSE](LICENSE).
