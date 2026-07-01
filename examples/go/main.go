package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"nhooyr.io/websocket"
	"nhooyr.io/websocket/wsjson"
)

const (
	baseURL = "http://localhost:8000"
	wsURL   = "ws://localhost:8000"
)

func sma(prices []float64, period int) (float64, bool) {
	if len(prices) < period {
		return 0, false
	}
	slice := prices[len(prices)-period:]
	var sum float64
	for _, p := range slice {
		sum += p
	}
	return sum / float64(period), true
}

func postJSON(url string, body any, target any) error {
	b, err := json.Marshal(body)
	if err != nil {
		return err
	}
	resp, err := http.Post(url, "application/json", bytes.NewReader(b))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return json.NewDecoder(resp.Body).Decode(target)
}

func getJSON(url string, target any) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return json.NewDecoder(resp.Body).Decode(target)
}

func main() {
	ctx := context.Background()

	// Create session
	var session struct {
		SessionID string `json:"session_id"`
	}
	if err := postJSON(baseURL+"/sessions", map[string]any{
		"symbols":      []string{"AAPL"},
		"start":        "2023-01-01",
		"end":          "2023-12-31",
		"capital":      10000.0,
		"data_adapter": "yfinance",
	}, &session); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Session created: %s\n", session.SessionID)

	// Connect WebSocket
	conn, _, err := websocket.Dial(ctx, wsURL+"/sessions/"+session.SessionID+"/stream", nil)
	if err != nil {
		log.Fatal(err)
	}
	defer conn.CloseNow()

	var prices []float64
	position := 0

	for {
		var msg map[string]any
		if err := wsjson.Read(ctx, conn, &msg); err != nil {
			break
		}
		eventType, _ := msg["type"].(string)
		data, _ := msg["data"].(map[string]any)

		switch eventType {
		case "BAR":
			close, _ := data["c"].(float64)
			symbol, _ := data["symbol"].(string)
			prices = append(prices, close)
			fast, okFast := sma(prices, 10)
			slow, okSlow := sma(prices, 20)
			if !okFast || !okSlow {
				continue
			}
			if fast > slow && position == 0 {
				_ = wsjson.Write(ctx, conn, map[string]any{
					"type": "ORDER",
					"data": map[string]any{"symbol": symbol, "side": "buy", "qty": 10, "order_type": "market"},
				})
				position = 1
				fmt.Printf("BUY  @ %.2f | fast=%.2f slow=%.2f\n", close, fast, slow)
			} else if fast < slow && position == 1 {
				_ = wsjson.Write(ctx, conn, map[string]any{
					"type": "ORDER",
					"data": map[string]any{"symbol": symbol, "side": "sell", "qty": 10, "order_type": "market"},
				})
				position = 0
				fmt.Printf("SELL @ %.2f | fast=%.2f slow=%.2f\n", close, fast, slow)
			}
		case "FILL":
			side, _ := data["side"].(string)
			qty, _ := data["qty"].(float64)
			price, _ := data["price"].(float64)
			fee, _ := data["fee"].(float64)
			fmt.Printf("  -> Fill: %s %.0f @ %.2f (fee=%.4f)\n", side, qty, price, fee)
		case "SESSION_END":
			fmt.Println("Session ended.")
			goto done
		}
	}
done:
	conn.Close(websocket.StatusNormalClosure, "done")

	// Final report
	var report map[string]any
	if err := getJSON(fmt.Sprintf("%s/sessions/%s/report", baseURL, session.SessionID), &report); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("\n=== Final Report ===\n")
	fmt.Printf("Sharpe:       %.4f\n", report["sharpe"])
	fmt.Printf("Max Drawdown: %.4f\n", report["max_drawdown"])
	fmt.Printf("VaR 95%%:      %.4f\n", report["var_95"])
	fmt.Printf("Total P&L:    $%.2f\n", report["total_pnl"])
	trades, _ := report["trades"].([]any)
	fmt.Printf("Trades:       %d\n", len(trades))
	os.Exit(0)
}
