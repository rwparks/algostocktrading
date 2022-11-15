import unittest
from typing import Any
from unittest import TestCase, skip
from unittest.mock import Mock
import pandas as pd
from pandas._testing import assert_frame_equal

from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.object_serialization import ObjectSerialization


class HistoricalDataProviderConcrete:
    def retrieve(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass


class PersistenceProviderConcrete:

    def load(self, file_name_format: str, **kwargs) -> Any:
        pass

    def save(self, data: Any, file_name_format: str, **kwargs) -> None:
        pass


class HistoricalDataFetcherTestCase(TestCase):

    def setUp(self):
        self.test_dataframe = pd.DataFrame([1, 2, 3], columns=['numbers'])
        self.data_provider = HistoricalDataProviderConcrete()
        self.data_provider.retrieve = Mock()
        self.persistence_provider = PersistenceProviderConcrete()
        self.persistence_provider.load = Mock()
        self.persistence_provider.save = Mock()

    @skip("skipping these because are not actual tests")
    def test_real_fetch(self):
        start_date = '20200101'
        end_date = '20200131'
        data_fetcher =\
            HistoricalDataFetcher(
                data_provider=Ameritrade(),
                persistence_provider=ObjectSerialization(persist_dir=f'./data/{start_date}-{end_date}'))
        data = data_fetcher.fetch(ticker='AAPL', start_date=start_date, end_date=end_date)
        print(data)

    def test_fetch_no_persistence_provider(self):
        self.data_provider.retrieve.return_value = self.test_dataframe
        data_fetcher = HistoricalDataFetcher(data_provider=self.data_provider)

        assert_frame_equal(data_fetcher.fetch(ticker='A', start_date='20220822', end_date='20220826'),
                           self.test_dataframe)

    def test_fetch_persistence_provider_and_refresh(self):
        self.data_provider.retrieve.return_value = self.test_dataframe
        data_fetcher = HistoricalDataFetcher(data_provider=self.data_provider,
                                             persistence_provider=self.persistence_provider,
                                             refresh=True)

        assert_frame_equal(data_fetcher.fetch(ticker='A', start_date='20220822', end_date='20220826'),
                           self.test_dataframe)
        self.assertEqual(self.data_provider.retrieve.call_count, 1)
        self.assertEqual(self.persistence_provider.load.call_count, 0)
        self.assertEqual(self.persistence_provider.save.call_count, 1)

    def test_fetch_persistence_provider_and_no_refresh(self):
        self.persistence_provider.load.return_value = self.test_dataframe
        data_fetcher = HistoricalDataFetcher(data_provider=self.data_provider,
                                             persistence_provider=self.persistence_provider)

        assert_frame_equal(data_fetcher.fetch(ticker='A', start_date='20220822', end_date='20220826'),
                           self.test_dataframe)
        self.assertEqual(self.data_provider.retrieve.call_count, 0)
        self.assertEqual(self.persistence_provider.load.call_count, 1)
        self.assertEqual(self.persistence_provider.save.call_count, 0)


if __name__ == '__main__':
    unittest.main()
