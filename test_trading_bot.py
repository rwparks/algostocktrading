import pickle
from datetime import datetime, timedelta
from unittest import TestCase

import pandas as pd

from brokerage.apiclient.interactivebrokers.ibclient import IBClient
from brokerage.brokerage_service import BrokerageService
from brokerage.ib_brokerage_service import IBBrokerageService
from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.historical_data_provider import HistoricalDataProvider
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider
from prediction.lr_prediction_provider import LRPredictionProvider
from trading.positions import Positions
from trading.prediction_trader import PredictionTrader
from trading.trader import Trader
from trading_bot import TradingBot


def is_sell_trigger(price: float, quote: float, enter_day: datetime) -> bool:
    gain_target_met = quote > (price + (price * 0.04))
    loss_target_met = quote < (price - (price * 0.003))
    held_time_exceeded = enter_day + timedelta(days=10) <= datetime.now()
    return gain_target_met or loss_target_met or held_time_exceeded


class TradingBotTestCase(TestCase):

    def test_real(self):
        historical_data_provider: HistoricalDataProvider = Ameritrade()
        broker: BrokerageService = IBBrokerageService(client=IBClient(port='5100'))
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                        persistence_provider=persistence_provider)

        classifier = pickle.load(open('daily_LR_stocks_v5.clfr', 'rb'))
        scaler = pickle.load(open('daily_LR_stocks_v5.sclr', 'rb'))
        predictor = LRPredictionProvider(classifier=classifier,
                                         scaler=scaler,
                                         historical_data_fetcher=historical_data_fetcher,
                                         #end_date=end_date
                                         )

        #stocks = pd.read_csv('scores_list_a.csv')['ticker'].values.tolist()[:50]

        with open('best_scores.lst', 'r+') as f:
            stocks = f.read().splitlines()[:50]

        trader: Trader = PredictionTrader(tickers=stocks,
                                          broker=broker,
                                          #positions=positions,
                                          predictor=predictor)

        positions = Positions(dir='./data').load()

        trading_bot = TradingBot(trader=trader, is_sell_trigger=is_sell_trigger)

        positions = trading_bot.execute(positions=positions, end_date=datetime(2022, 11, 11))

        positions.save()

        print(positions)