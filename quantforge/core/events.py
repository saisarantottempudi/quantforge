from enum import Enum


class EventType(str, Enum):
    BAR = "BAR"
    ORDER = "ORDER"
    CANCEL = "CANCEL"
    FILL = "FILL"
    PORTFOLIO_TICK = "PORTFOLIO_TICK"
    SESSION_END = "SESSION_END"
    ERROR = "ERROR"
