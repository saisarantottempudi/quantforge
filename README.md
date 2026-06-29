# QuantForge

Language-agnostic backtesting and paper trading engine.

Strategy logic runs in **your client** (any language). The engine handles data, simulation, portfolio tracking, and observability.

## Status

Under active development

## Quickstart

```bash
docker compose up
```

Then connect any WebSocket client to `ws://localhost:8000/sessions/{id}/stream`.

## Architecture

```
Client (Python / Go / Rust / TS / anything)
   |  WebSocket  <- BAR, FILL, PORTFOLIO_TICK events
   |  REST       <- session control, portfolio queries, reports
         |
   QuantForge Engine (Python + FastAPI + asyncio)
```

## Data Adapters

| Adapter | Asset Class | API Key Required |
|---|---|---|
| `yfinance` | Equities, ETFs | No |
| `ccxt` | Crypto (100+ exchanges) | No (public endpoints) |
| `forex` | Forex pairs | Yes — Alpha Vantage free tier |
| `synthetic` | Any (test/demo) | No |

Set `ALPHA_VANTAGE_KEY` env var for forex (free tier: 5 req/min, 500/day).

## Core Concepts

- **Bar** — OHLCV candlestick with symbol, timestamp, and asset class
- **Order** — client-submitted buy/sell with qty and type (market/limit)
- **Fill** — engine-generated execution confirmation with fill price and fee
- **Session** — isolated backtest or paper trading run with its own config and portfolio
- **BarEmitter** — replays historical bars in chronological order across all symbols in a session

## Portfolio Metrics

Available in `GET /sessions/{id}/report` after session completes:

| Metric | Description |
|---|---|
| `total_pnl` | Total profit/loss in dollars |
| `sharpe` | Annualized Sharpe ratio (daily returns, rf=0) |
| `max_drawdown` | Maximum peak-to-trough equity drawdown |
| `var_95` / `var_99` | Value at Risk at 95% / 99% confidence |
| `equity_curve` | Equity value at each bar |
| `trades` | Full fill log |

## Session Lifecycle

```
created → running → completed
                 ↘ error
```

Sessions are isolated asyncio tasks. Multiple can run concurrently. Each has its own equity curve, fill log, and pending orders queue.

## Observability

Built-in, zero-config:

- **Prometheus metrics** at `GET /metrics`: sessions active, bars emitted, orders received, fills, data fetch latency
- **Structured JSON logs** via structlog (session_id + asset_class tagged on every event)

Start with Prometheus + Grafana pre-wired:
```bash
docker compose -f docker-compose.observability.yml up
```
Grafana: http://localhost:3000

## REST API

Interactive docs at http://localhost:8000/docs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sessions` | Create a session → `{session_id, ws_url}` |
| `GET` | `/sessions/{id}` | Session state + config |
| `DELETE` | `/sessions/{id}` | Stop and remove session |
| `GET` | `/sessions/{id}/portfolio` | Current positions, cash, equity |
| `GET` | `/sessions/{id}/report` | Full report (Sharpe, VaR, drawdown, trades) |
| `GET` | `/sessions/{id}/trades` | Fill log |
| `GET` | `/sessions/{id}/orders` | Pending orders |
| `GET` | `/health` | Liveness check |
| `GET` | `/metrics` | Prometheus metrics |
| `WS` | `/sessions/{id}/stream` | Bar stream + order submission |

## License

Apache 2.0
