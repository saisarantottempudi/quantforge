from datetime import datetime, UTC
from enum import Enum
from typing import Literal
import uuid
from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITY = "equity"
    CRYPTO = "crypto"
    FOREX = "forex"
    FUTURES = "futures"


class Bar(BaseModel):
    symbol: str
    ts: datetime
    o: float
    h: float
    l: float
    c: float
    v: float
    asset_class: AssetClass = AssetClass.EQUITY


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    side: OrderSide
    qty: float
    order_type: OrderType = OrderType.MARKET
    price: float | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Fill(BaseModel):
    order_id: str
    symbol: str
    side: OrderSide
    qty: float
    fill_price: float
    fee: float
    ts: datetime


class Position(BaseModel):
    symbol: str
    qty: float
    avg_cost: float


class SessionMode(str, Enum):
    BACKTEST = "backtest"
    PAPER = "paper"


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class SlippageConfig(BaseModel):
    model: Literal["fixed_bps", "percent", "volume_proportional"] = "fixed_bps"
    value: float = 5.0


class FeeConfig(BaseModel):
    model: Literal["flat_per_trade", "percent"] = "percent"
    value: float = 0.001


class SessionConfig(BaseModel):
    mode: SessionMode = SessionMode.BACKTEST
    symbols: list[str]
    start: str
    end: str
    timeframe: str = "1d"
    capital: float = 100_000.0
    slippage: SlippageConfig = Field(default_factory=SlippageConfig)
    fees: FeeConfig = Field(default_factory=FeeConfig)
    data_adapter: Literal["yfinance", "ccxt", "forex", "synthetic"] = "yfinance"
    portfolio_tick_interval: int = 1
