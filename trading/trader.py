from datetime import datetime
from typing import Protocol, Callable

from brokerage.brokerage_service import BrokerageService
from trading.positions import Positions
from trading.prediction_bucket import PredictionBucket


class Trader(Protocol):
    broker: BrokerageService
    buy_prediction_bucket: PredictionBucket
    sell_prediction_bucket: PredictionBucket

    def build_prediction_buckets(self, end_date: datetime):
        """ build prediction """

    def check_sell(self, positions: Positions, sell_trigger: Callable[..., bool]):
        """ should sell """

    def check_buy(self, positions: Positions, cash: float):
        """ should buy """
