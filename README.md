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

## License

Apache 2.0
