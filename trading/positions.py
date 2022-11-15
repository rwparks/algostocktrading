import logging
import os
import pickle
from collections import UserDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from datautils.persistence_provider import PersistenceProvider
#from setup_logger import logger


@dataclass
class PositionValues:
    quantity: int
    enter_day: datetime
    price: Optional[float] = None
    order_id: str = None


SAVE_PATH = r'positions.pkl'


class Positions(UserDict):

    def __init__(self, persistence_provider: PersistenceProvider, max_positions=1, **kwargs):
        super().__init__(**kwargs)
        self.persistence_provider = persistence_provider
        self.max_positions = max_positions
        self.logger = logging.getLogger(__name__)

    def load(self):
        positions = self.persistence_provider.load(file_name_format='positions.pkl')
        if positions:
            return positions
        else:
            return self

    def __setitem__(self, key, value):
        if len(self.data) < self.max_positions:
            return self.data.__setitem__(key, value)
        raise RuntimeWarning

    @property
    def available(self) -> int:
        return self.max_positions - len(self.data)

    def save(self):
        self.persistence_provider.save(data=self, file_name_format='positions.pkl')
