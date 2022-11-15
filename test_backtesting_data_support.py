from unittest import TestCase

from backtesting_data_support import BacktestingDataSupport
from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider


class BackingtestingDataSupportTestCase(TestCase):

    def test_real(self):
        start_date = '20200101'
        end_date = '20211231'
        persist_dir = f'./backtesting_data/{start_date}-{end_date}'

        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir=persist_dir)

        data_fetcher: HistoricalDataFetcher = HistoricalDataFetcher(data_provider=Ameritrade(),
                                                                    persistence_provider=persistence_provider)

        backtesting_data_support = BacktestingDataSupport(start_date=start_date,
                                                          end_date=end_date,
                                                          data_fetcher=data_fetcher,
                                                          persistence_provider=persistence_provider)

        print(backtesting_data_support.day_list)
        print(backtesting_data_support.close_series(ticker='A'))
