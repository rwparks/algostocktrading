# import datetime
# import datetime
import logging.config
import pickle
from datetime import timedelta, datetime

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


def is_sell_trigger(price: float, quote: float, enter_day: datetime) -> bool:
    gain_target_met = quote > (price + (price * 0.04))
    loss_target_met = quote < (price - (price * 0.003))
    held_time_exceeded = enter_day + timedelta(days=10) <= datetime.now()
    return gain_target_met or loss_target_met or held_time_exceeded


day_hist_format = 'day_{ticker}_{start_date}-{end_date}.pkl'

stocks = pd.read_csv('scores_list_a.csv')['ticker'].values.tolist()[:50]

historical_data_provider: HistoricalDataProvider = Ameritrade()

logging.config.fileConfig('bot.logconf')
logger = logging.getLogger('bot')

# print(stocks)


def execute(persist_dir: str,
            clfr: str,
            sclr: str,
            end_date: datetime = datetime.now(),
            persist_hist_data: bool = True,
            backtesting: bool = False):
    broker: BrokerageService = IBBrokerageService(client=IBClient(port='5100'))
    #persistence_provider: PersistenceProvider = ObjectSerialization(file_name_format=day_hist_format,
    #                                                                persist_dir=persist_dir)
    persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir=persist_dir)
    historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                    persistence_provider=persistence_provider)

    classifier = pickle.load(open(clfr, 'rb'))
    scaler = pickle.load(open(sclr, 'rb'))
    predictor = LRPredictionProvider(classifier=classifier,
                                     scaler=scaler,
                                     historical_data_fetcher=historical_data_fetcher,
                                     end_date=end_date)

    positions = Positions()
    positions.load()
    logger.info(f'positions: {positions}')

    trader: Trader = PredictionTrader(tickers=stocks,
                                      broker=broker,
                                      positions=positions,
                                      predictor=predictor)

    logger.info(trader.buy_prediction_bucket.sorted_get(0))
    logger.info(trader.sell_prediction_bucket)

    trader.check_sell(sell_trigger=is_sell_trigger)

    #cash = broker.get_cash_value();
    cash = 10000.00
    trader.check_buy(cash=round(cash, 2))

    print(f'positions: {positions}')
    positions.save()


execute(persist_dir='./data',
        clfr='daily_LR_stocks_v5.clfr',
        sclr='daily_LR_stocks_v5.sclr')
