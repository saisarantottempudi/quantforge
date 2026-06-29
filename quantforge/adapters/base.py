from abc import ABC, abstractmethod
from typing import AsyncIterator
from quantforge.core.models import Bar


class DataAdapter(ABC):
    @abstractmethod
    async def get_bars(
        self,
        symbol: str,
        start: str,
        end: str,
        timeframe: str,
    ) -> AsyncIterator[Bar]:
        ...
