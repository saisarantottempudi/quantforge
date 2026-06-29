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

## License

Apache 2.0
