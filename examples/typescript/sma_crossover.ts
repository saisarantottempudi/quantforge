import WebSocket from "ws";

const BASE_URL = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

function sma(prices: number[], period: number): number | null {
  if (prices.length < period) return null;
  const slice = prices.slice(-period);
  return slice.reduce((a, b) => a + b, 0) / period;
}

async function postJSON<T>(url: string, body: unknown): Promise<T> {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`POST ${url} -> ${resp.status}`);
  return resp.json() as Promise<T>;
}

async function getJSON<T>(url: string): Promise<T> {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`GET ${url} -> ${resp.status}`);
  return resp.json() as Promise<T>;
}

async function run(): Promise<void> {
  const session = await postJSON<{ session_id: string }>(`${BASE_URL}/sessions`, {
    symbols: ["AAPL"],
    start: "2023-01-01",
    end: "2023-12-31",
    capital: 10000.0,
    data_adapter: "yfinance",
  });
  console.log(`Session created: ${session.session_id}`);

  const prices: number[] = [];
  let position = 0;

  await new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`${WS_BASE}/sessions/${session.session_id}/stream`);

    ws.on("message", (raw: WebSocket.RawData) => {
      const msg = JSON.parse(raw.toString()) as { type: string; data: Record<string, unknown> };

      if (msg.type === "BAR") {
        const bar = msg.data as { symbol: string; c: number };
        prices.push(bar.c);
        const fast = sma(prices, 10);
        const slow = sma(prices, 20);
        if (fast === null || slow === null) return;

        if (fast > slow && position === 0) {
          ws.send(JSON.stringify({
            type: "ORDER",
            data: { symbol: bar.symbol, side: "buy", qty: 10, order_type: "market" },
          }));
          position = 1;
          console.log(`BUY  @ ${bar.c.toFixed(2)} | fast=${fast.toFixed(2)} slow=${slow.toFixed(2)}`);
        } else if (fast < slow && position === 1) {
          ws.send(JSON.stringify({
            type: "ORDER",
            data: { symbol: bar.symbol, side: "sell", qty: 10, order_type: "market" },
          }));
          position = 0;
          console.log(`SELL @ ${bar.c.toFixed(2)} | fast=${fast.toFixed(2)} slow=${slow.toFixed(2)}`);
        }
      } else if (msg.type === "FILL") {
        const fill = msg.data as { side: string; qty: number; price: number; fee: number };
        console.log(`  -> Fill: ${fill.side} ${fill.qty} @ ${fill.price.toFixed(2)} (fee=${fill.fee.toFixed(4)})`);
      } else if (msg.type === "SESSION_END") {
        console.log("Session ended.");
        ws.close();
        resolve();
      }
    });

    ws.on("error", reject);
  });

  const report = await getJSON<{
    sharpe: number;
    max_drawdown: number;
    var_95: number;
    total_pnl: number;
    trades: unknown[];
  }>(`${BASE_URL}/sessions/${session.session_id}/report`);

  console.log("\n=== Final Report ===");
  console.log(`Sharpe:        ${report.sharpe.toFixed(4)}`);
  console.log(`Max Drawdown:  ${report.max_drawdown.toFixed(4)}`);
  console.log(`VaR 95%:       ${report.var_95.toFixed(4)}`);
  console.log(`Total P&L:     $${report.total_pnl.toFixed(2)}`);
  console.log(`Trades:        ${report.trades.length}`);
}

run().catch(console.error);
