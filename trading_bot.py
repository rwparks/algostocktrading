import logging
from logging import Logger
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

from brokerage.brokerage_service import BrokerageService
from datautils.persistence_provider import PersistenceProvider
from trading.positions import Positions
from trading.trader import Trader


@dataclass
class TradingBot:
    trader: Trader
    is_sell_trigger: Callable
    logger: Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, positions: Positions, end_date: datetime) -> Positions:
        #positions = Positions(dir='./data').load()
        #positions.load()
        self.logger.info(f'positions: {positions}')

        self.trader.build_prediction_buckets(end_date=end_date)

        self.logger.info(self.trader.buy_prediction_bucket.sorted_get(0))
        self.logger.info(self.trader.sell_prediction_bucket)

        self.trader.check_sell(positions=positions, sell_trigger=self.is_sell_trigger)

        # cash = broker.get_cash_value();
        cash = 10000.00
        self.trader.check_buy(positions=positions, cash=round(cash, 2))

        print(f'positions: {positions}')
        #positions.save()
        return positions
