# Contributing to QuantForge

Thank you for contributing! Here's what you need to know.

## Setup

```bash
git clone https://github.com/saisarantottempudi/quantforge.git
cd quantforge
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Development workflow

1. **Write tests first** — add to `tests/unit/` or `tests/integration/`
2. **Implement** — keep modules focused (one responsibility per file)
3. **Lint** — `ruff check quantforge/ tests/`
4. **Security** — `bandit -r quantforge/ -ll`
5. **Run suite** — `pytest tests/ -v`
6. **Commit** — conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)

## Project structure

```
quantforge/
  core/        # Pydantic models + event types
  adapters/    # DataAdapter ABC + yfinance / ccxt / forex / synthetic
  engine/      # BarEmitter, PaperBroker, PortfolioTracker, SessionManager
  api/         # FastAPI app, REST routes, WebSocket handler
  observability/ # Prometheus metrics, structlog setup
tests/
  unit/        # Fast, no I/O, mocked adapters
examples/
  python/      # SMA crossover (asyncio + websockets)
  go/          # SMA crossover (nhooyr.io/websocket)
  typescript/  # SMA crossover (ws + ts-node)
```

## Adding a new data adapter

1. Create `quantforge/adapters/your_adapter.py`
2. Subclass `DataAdapter` and implement `get_bars()`
3. Return `Bar` objects with correct `asset_class`
4. Register in `quantforge/api/routes.py` `_get_adapter()`
5. Add mocked unit tests (no real API calls in CI)

## Adding a new example client

Create `examples/<language>/` with a README snippet showing how to run it. Implement the same SMA(10/20) crossover so examples stay comparable.

## WebSocket protocol

**Engine → Client:**
```json
{"type": "BAR",            "data": {"symbol": "AAPL", "ts": "...", "o": 1, "h": 1, "l": 1, "c": 1, "v": 1}}
{"type": "FILL",           "data": {"order_id": "...", "symbol": "AAPL", "side": "buy", "qty": 10, "price": 150.0, "fee": 0.15}}
{"type": "PORTFOLIO_TICK", "data": {"cash": 8500.0, "equity": 10000.0, "positions": {...}}}
{"type": "SESSION_END",    "data": {"reason": "data_exhausted"}}
```

**Client → Engine:**
```json
{"type": "ORDER", "data": {"symbol": "AAPL", "side": "buy", "qty": 10, "order_type": "market"}}
```

## Running with Docker

```bash
# Engine only
docker compose up --build

# Engine + Prometheus + Grafana
docker compose -f docker-compose.observability.yml up --build
```

## Code style

- Line length: 100 characters
- Python 3.12+ features encouraged (union types, `datetime.now(UTC)`)
- No unnecessary comments — code should be self-documenting
- Pydantic v2 models for all data contracts

## License

Apache-2.0. Contributions are licensed under the same terms.
