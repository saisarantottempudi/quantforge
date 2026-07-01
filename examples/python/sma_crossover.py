#!/usr/bin/env python3
"""SMA(10/20) crossover strategy — connects to a running QuantForge engine."""
import asyncio
import json
import httpx
import websockets

BASE_URL = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"


def sma(prices: list[float], period: int) -> float | None:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


async def run():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.post("/sessions", json={
            "symbols": ["AAPL"],
            "start": "2023-01-01",
            "end": "2023-12-31",
            "capital": 10000.0,
            "data_adapter": "yfinance",
        })
        resp.raise_for_status()
        session = resp.json()
        session_id = session["session_id"]
        print(f"Session created: {session_id}")

    prices: list[float] = []
    position = 0

    uri = f"{WS_BASE}/sessions/{session_id}/stream"
    async with websockets.connect(uri) as ws:
        async for raw in ws:
            msg = json.loads(raw)
            event_type = msg["type"]

            if event_type == "BAR":
                bar = msg["data"]
                prices.append(bar["c"])
                fast = sma(prices, 10)
                slow = sma(prices, 20)
                if fast is None or slow is None:
                    continue

                if fast > slow and position == 0:
                    await ws.send(json.dumps({
                        "type": "ORDER",
                        "data": {"symbol": bar["symbol"], "side": "buy", "qty": 10, "order_type": "market"},
                    }))
                    position = 1
                    print(f"BUY  @ {bar['c']:.2f} | fast={fast:.2f} slow={slow:.2f}")

                elif fast < slow and position == 1:
                    await ws.send(json.dumps({
                        "type": "ORDER",
                        "data": {"symbol": bar["symbol"], "side": "sell", "qty": 10, "order_type": "market"},
                    }))
                    position = 0
                    print(f"SELL @ {bar['c']:.2f} | fast={fast:.2f} slow={slow:.2f}")

            elif event_type == "FILL":
                fill = msg["data"]
                print(f"  -> Fill: {fill['side']} {fill['qty']} @ {fill['price']:.2f} (fee={fill['fee']:.4f})")

            elif event_type == "SESSION_END":
                print("Session ended.")
                break

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        report = (await client.get(f"/sessions/{session_id}/report")).json()
    print(f"\n=== Final Report ===")
    print(f"Sharpe:        {report['sharpe']:.4f}")
    print(f"Max Drawdown:  {report['max_drawdown']:.4f}")
    print(f"VaR 95%:       {report['var_95']:.4f}")
    print(f"Total P&L:     ${report['total_pnl']:.2f}")
    print(f"Trades:        {len(report['trades'])}")


if __name__ == "__main__":
    asyncio.run(run())
