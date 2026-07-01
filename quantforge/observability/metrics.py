from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

sessions_active = Gauge("quantforge_sessions_active", "Active sessions")
bars_emitted = Counter(
    "quantforge_bars_emitted_total", "Total bars emitted", ["adapter", "asset_class"]
)
orders_received = Counter(
    "quantforge_orders_received_total", "Total orders received"
)
fills_total = Counter("quantforge_fills_total", "Total fills", ["side"])
data_fetch_latency = Histogram(
    "quantforge_data_fetch_latency_seconds", "Data fetch latency", ["adapter"]
)


def setup_metrics(app: FastAPI) -> None:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
