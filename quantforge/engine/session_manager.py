import asyncio
import uuid
from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Fill, Order, SessionConfig, SessionStatus
from quantforge.engine.broker import PaperBroker
from quantforge.engine.emitter import BarEmitter
from quantforge.engine.portfolio import PortfolioTracker


class Session:
    def __init__(self, session_id: str, config: SessionConfig, adapter: DataAdapter):
        self.session_id = session_id
        self.config = config
        self.status = SessionStatus.CREATED
        self._emitter = BarEmitter(adapter, config)
        self._broker = PaperBroker(config.slippage, config.fees)
        self._portfolio = PortfolioTracker(config.capital)
        self._pending_orders: list[Order] = []
        self._fills: list[Fill] = []
        self._bar_count = 0
        self.bar_queue: asyncio.Queue = asyncio.Queue()
        self.fill_queue: asyncio.Queue = asyncio.Queue()
        self.portfolio_queue: asyncio.Queue = asyncio.Queue()
        self.end_event: asyncio.Event = asyncio.Event()

    def submit_order(self, order: Order) -> None:
        self._pending_orders.append(order)

    async def run(self) -> None:
        self.status = SessionStatus.RUNNING
        try:
            current_prices: dict[str, float] = {}
            async for bar in self._emitter.emit():
                await self.bar_queue.put(bar)
                current_prices[bar.symbol] = bar.c
                unfilled = []
                for order in self._pending_orders:
                    if order.symbol == bar.symbol:
                        fill = self._broker.fill(order, bar)
                        self._fills.append(fill)
                        self._portfolio.apply_fill(fill)
                        await self.fill_queue.put(fill)
                    else:
                        unfilled.append(order)
                self._pending_orders = unfilled
                self._bar_count += 1
                self._portfolio.update_prices(current_prices)
                if self._bar_count % self.config.portfolio_tick_interval == 0:
                    await self.portfolio_queue.put(self._portfolio.snapshot())
            self.status = SessionStatus.COMPLETED
        except Exception:
            self.status = SessionStatus.ERROR
            raise
        finally:
            self.end_event.set()

    def portfolio_snapshot(self) -> dict:
        return self._portfolio.snapshot()

    def report(self) -> dict:
        return {
            "session_id": self.session_id,
            "status": self.status,
            "sharpe": self._portfolio.sharpe(),
            "max_drawdown": self._portfolio.max_drawdown(),
            "var_95": self._portfolio.var(0.95),
            "var_99": self._portfolio.var(0.99),
            "total_pnl": self._portfolio.total_pnl(),
            "trades": [f.model_dump(mode="json") for f in self._fills],
            "equity_curve": self._portfolio._equity_curve,
        }

    def fills(self) -> list[dict]:
        return [f.model_dump(mode="json") for f in self._fills]

    def pending_orders(self) -> list[dict]:
        return [o.model_dump(mode="json") for o in self._pending_orders]


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create(self, config: SessionConfig, adapter: DataAdapter) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id, config, adapter)
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.status == SessionStatus.RUNNING)
