import asyncio
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from quantforge.adapters.ccxt_adapter import CCXTAdapter
from quantforge.adapters.forex_adapter import ForexAdapter
from quantforge.adapters.synthetic import SyntheticAdapter
from quantforge.adapters.yfinance_adapter import YFinanceAdapter
from quantforge.core.events import EventType
from quantforge.core.models import Order, OrderSide, OrderType, SessionConfig

router = APIRouter()


def _get_adapter(name: str):
    if name == "yfinance":
        return YFinanceAdapter()
    if name == "ccxt":
        return CCXTAdapter()
    if name == "forex":
        return ForexAdapter()
    return SyntheticAdapter()


@router.post("/sessions")
async def create_session(config: SessionConfig, request: Request):
    sm = request.app.state.session_manager
    adapter = _get_adapter(config.data_adapter)
    session = sm.create(config, adapter)
    asyncio.create_task(session.run())
    return {"session_id": session.session_id, "ws_url": f"/sessions/{session.session_id}/stream"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, request: Request):
    session = request.app.state.session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "status": session.status, "config": session.config.model_dump()}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    if not request.app.state.session_manager.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": session_id}


@router.get("/sessions/{session_id}/portfolio")
async def get_portfolio(session_id: str, request: Request):
    session = request.app.state.session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.portfolio_snapshot()


@router.get("/sessions/{session_id}/report")
async def get_report(session_id: str, request: Request):
    session = request.app.state.session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.report()


@router.get("/sessions/{session_id}/trades")
async def get_trades(session_id: str, request: Request):
    session = request.app.state.session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.fills()


@router.get("/sessions/{session_id}/orders")
async def get_orders(session_id: str, request: Request):
    session = request.app.state.session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.pending_orders()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.websocket("/sessions/{session_id}/stream")
async def ws_stream(websocket: WebSocket, session_id: str):
    sm = websocket.app.state.session_manager
    session = sm.get(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    await websocket.accept()

    async def drain_queues():
        while True:
            done = session.end_event.is_set()
            for queue, etype in [
                (session.bar_queue, EventType.BAR),
                (session.fill_queue, EventType.FILL),
                (session.portfolio_queue, EventType.PORTFOLIO_TICK),
            ]:
                while not queue.empty():
                    item = queue.get_nowait()
                    payload = item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                    await websocket.send_json({"type": etype, "data": payload})
            if done and all(
                q.empty() for q in [session.bar_queue, session.fill_queue, session.portfolio_queue]
            ):
                return
            await asyncio.sleep(0.01)

    async def receive_orders():
        try:
            async for msg in websocket.iter_json():
                if msg.get("type") == EventType.ORDER:
                    d = msg["data"]
                    session.submit_order(Order(
                        symbol=d["symbol"],
                        side=OrderSide(d["side"]),
                        qty=d["qty"],
                        order_type=OrderType(d.get("order_type", "market")),
                        price=d.get("price"),
                    ))
        except (WebSocketDisconnect, Exception):
            pass

    drain_task = asyncio.create_task(drain_queues())
    recv_task = asyncio.create_task(receive_orders())
    await drain_task
    recv_task.cancel()
    try:
        await websocket.send_json({"type": EventType.SESSION_END, "data": {"reason": "data_exhausted"}})
        await websocket.close()
    except Exception:
        pass
