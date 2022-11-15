import os
import pickle
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import List, Protocol, Dict

from brokerage.apiclient.interactivebrokers.order_status_response import OrderStatusResponse

ACCOUNT_BALANCE_PATH = './account.txt'


@dataclass
class BackTestingBrokerageService:
    closing_prices: Dict

    def __post_init__(self):
        pass

    def place_order(self, side: str, ticker: str, quantity: int):
        account_balance: float = self.get_cash_value()
        resp = {
            'order_id': int(time() * 1000),
            'average_price': self.closing_prices[ticker] if side == 'SELL' else None,
            'order_status': 'Filled'
        }
        if side == 'BUY':
            account_balance = account_balance - (self.closing_prices[ticker] * quantity)
        else:
            account_balance = account_balance + (self.closing_prices[ticker] * quantity)

        with open(ACCOUNT_BALANCE_PATH, 'w') as f:
            print(account_balance, file=f)
        return OrderStatusResponse.construct(**resp)

    def place_orders(self, orders: Dict[str, List[Dict]]):
        pass

    def get_quote(self, ticker: str):
        pass

    def get_cash_value(self) -> float:
        if os.path.isfile(ACCOUNT_BALANCE_PATH):
            with open(ACCOUNT_BALANCE_PATH, 'r+') as f:
                return float(f.readline())

    def get_order_status(self, order_id: str):
        pass
