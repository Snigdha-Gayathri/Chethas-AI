from __future__ import annotations
from abc import ABC, abstractmethod
from ..models import RetrievalConfig, RetrievalResult

class BaseStrategy(ABC):
    name: str
    description: str
    
    @abstractmethod
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        ...
