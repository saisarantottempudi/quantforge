from fastapi import FastAPI
from quantforge.api.routes import router
from quantforge.engine.session_manager import SessionManager
from quantforge.observability.logging import setup_logging
from quantforge.observability.metrics import setup_metrics


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="QuantForge", version="0.1.0", description="Language-agnostic backtesting engine")
    app.state.session_manager = SessionManager()
    app.include_router(router)
    setup_metrics(app)
    return app


app = create_app()
