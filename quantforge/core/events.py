from enum import StrEnum


class EventType(StrEnum):
    BAR = "BAR"
    ORDER = "ORDER"
    CANCEL = "CANCEL"
    FILL = "FILL"
    PORTFOLIO_TICK = "PORTFOLIO_TICK"
    SESSION_END = "SESSION_END"
    ERROR = "ERROR"
