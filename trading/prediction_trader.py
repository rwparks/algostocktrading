import logging
from logging import Logger
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable

from brokerage.apiclient.interactivebrokers.order_status_response import OrderStatusResponse
from brokerage.brokerage_service import BrokerageService, OrderSide
from prediction.prediction_provider import PredictionProvider

#from setup_logger import logger

from .prediction_bucket import PredictionBucket
from .positions import Positions, PositionValues


@dataclass
class PredictionTrader:
    tickers: List[str]
    broker: BrokerageService
    predictor: PredictionProvider
    #positions: Positions = field(init=False, default_factory=Positions)
    #positions: Positions
    buy_prediction_bucket: PredictionBucket = field(init=False, default_factory=PredictionBucket)
    sell_prediction_bucket: PredictionBucket = field(init=False, default_factory=PredictionBucket)
    logger: Logger = field(init=False)

    def __post_init__(self):
        #loaded_positions = self.positions.load()
        #self.positions = loaded_positions if loaded_positions is not None else self.positions
        #self._build_prediction_buckets()
        self.logger = logging.getLogger(__name__)

    def build_prediction_buckets(self, end_date: datetime):
        for ticker in self.tickers:
            #prediction = self.predictor.predict(ticker=ticker)
            prediction = self.predictor.predict(ticker=ticker, end_date=end_date)
            # A label of 0 indicates a buy signal
            if prediction.label == 0:
                self.buy_prediction_bucket[ticker] = prediction
            else:
                self.sell_prediction_bucket[ticker] = prediction

    #def check_sell(self, sell_trigger: Callable[..., bool]):
    def check_sell(self, positions: Positions, sell_trigger: Callable[..., bool]):
        positions_to_delete = []
        #for ticker, position in self.positions.items():
        for ticker, position in positions.items():
            quote = self.broker.get_quote(ticker=ticker)
            is_triggered = sell_trigger(price=position.price, quote=quote, enter_day=position.enter_day)
            if ticker in self.sell_prediction_bucket or is_triggered:
                resp: OrderStatusResponse = self.broker.place_order(side=OrderSide.SELL,
                                                                    ticker=ticker,
                                                                    quantity=position.quantity)
                if resp.order_status == 'Filled':
                    positions_to_delete.append(ticker)
                else:
                    # TODO: log message about order not being filled
                    self.logger.warning(f'PredictionTrader.check_sell: order could not be filled: {resp}')
                    #pass

        for t in positions_to_delete:
            #del self.positions[t]
            del positions[t]

    #def check_buy(self, cash: float):
    def check_buy(self, positions: Positions, cash: float):
        buy_bucket_length = len(self.buy_prediction_bucket)
        #positions_to_be_filled = buy_bucket_length if buy_bucket_length < self.positions.available else \
        #    self.positions.available
        positions_to_be_filled = buy_bucket_length if buy_bucket_length < positions.available else \
            positions.available
        if positions_to_be_filled > 0:
            amount_dollars = cash / positions_to_be_filled
            for i in range(0, positions_to_be_filled):
                try:
                    ticker = self.buy_prediction_bucket.sorted_get(i)
                    price = self.broker.get_quote(ticker=ticker).ask
                    quantity = int(amount_dollars / price)
                    if quantity > 0:
                        #resp: OrderStatusResponse = self.broker.place_order(side=OrderSide.BUY,
                        resp: OrderStatusResponse = self.broker.place_order(side='BUY',
                                                                            ticker=ticker,
                                                                            quantity=quantity)
                        if resp.order_status == 'Filled':
                            #self.positions[ticker] = PositionValues(order_id=str(resp.order_id),
                            positions[ticker] = PositionValues(order_id=str(resp.order_id),
                                                               quantity=quantity,
                                                               price=float(resp.average_price),
                                                               enter_day=datetime.now())
                        else:
                            # TODO: log message about order not being filled
                            self.logger.warning(f'PredictionTrader.check_buy: order could not be filled: {resp}')
                            #pass

                except IndexError:
                    break
