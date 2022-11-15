import pickle
import unittest
from datetime import datetime
from unittest import mock, TestCase, skip
from unittest.mock import patch, Mock

import numpy
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.historical_data_provider import HistoricalDataProvider
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider
from features.features import normalized_values, n_day_regression
from prediction.lr_prediction_provider import LRPredictionProvider


class HistoricalDataProviderConcrete:
    def retrieve(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass


class PersistenceProviderConcrete:

    def load(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass

    def save(self, data: pd.DataFrame, ticker: str, start_date: str, end_date: str) -> None:
        pass


class LRPredictionProviderTestCase(TestCase):

    def setUp(self):
        historical_data_provider: HistoricalDataProvider = HistoricalDataProviderConcrete()
        historical_data_provider.retrieve = Mock()
        persistence_provider: PersistenceProvider = PersistenceProviderConcrete()
        persistence_provider.load = Mock()
        persistence_provider.save = Mock()
        historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                        persistence_provider=persistence_provider)
        historical_data_fetcher.fetch = Mock()
        self.prediction_provider = LRPredictionProvider(classifier=Mock(),
                                                        scaler=Mock(),
                                                        historical_data_fetcher=historical_data_fetcher)

    #@mock.patch('prediction.lr_prediction_provider.datetime')
    def test__get_features_data(self, mock_datetime):
        df = pd.DataFrame(data=[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9],
                                [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17],
                                [18, 18],
                                [19, 19], [20, 20], [21, 21]],
                          columns=['a', 'b'])
        df.set_index(keys='a', inplace=True)
        expected_result = df[:].copy(deep=True).reset_index()
        #mock_datetime.now = Mock(return_value=datetime(2022, 8, 10))
        self.prediction_provider.historical_data_fetcher.fetch.return_value = df

        result = self.prediction_provider._get_features_data(ticker='A', end_date=datetime(2022, 8, 10))

        assert_frame_equal(expected_result, result)

    @mock.patch('prediction.lr_prediction_provider.datetime')
    @mock.patch('prediction.lr_prediction_provider.features_for_production')
    def test_predict_returns_correct_namedtuple(self, mock_features_for_production, mock_datetime):
        self.prediction_provider.classifier.predict.return_value = [0]
        self.prediction_provider.classifier.predict_probability.return_value = numpy.full((1, 2), [0.95, 0.5])
        self.prediction_provider.scaler.transform.return_value = None
        self.prediction_provider._get_features_data = Mock(return_value=pd.DataFrame())
        mock_datetime.now = Mock(return_value=datetime(2022, 8, 10))
        mock_features_for_production.return_value = pd.DataFrame()

        result = self.prediction_provider.predict('A')

        assert result.label == 0
        assert result.probability == 0.95


@skip("skipping these because are not actual tests")
class LRPredictionProviderRealDataTestCase(TestCase):

    @staticmethod
    def test_real_predict():
        historical_data_provider: HistoricalDataProvider = Ameritrade()
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                        persistence_provider=persistence_provider)
        classifier = pickle.load(open('daily_LR_stocks_v5.clfr', 'rb'))
        scaler = pickle.load(open('daily_LR_stocks_v5.sclr', 'rb'))
        lr_prediction_provider = LRPredictionProvider(classifier=classifier,
                                                      scaler=scaler,
                                                      historical_data_fetcher=historical_data_fetcher)
        print(lr_prediction_provider.predict('L'))

    @staticmethod
    def test_real_feature_generation_process():
        historical_data_provider: HistoricalDataProvider = Ameritrade()
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                        persistence_provider=persistence_provider)
        classifier = pickle.load(open('daily_LR_stocks_v5.clfr', 'rb'))
        scaler = pickle.load(open('daily_LR_stocks_v5.sclr', 'rb'))
        lr_prediction_provider = LRPredictionProvider(classifier=classifier,
                                                      scaler=scaler,
                                                      historical_data_fetcher=historical_data_fetcher)

        pd.set_option('display.max_columns', None, 'display.width', 160)
        # Get historical data to feed in the feature generation process.  By default it retrieves from the
        #  last 40 calendar days.  We need at least 20 trading days. But 40 calendar day is more than to account
        #  for days in which the market is closed.
        data = lr_prediction_provider._get_features_data('L', datetime(2022, 11, 11))
        print(data)
        # Add the normalized_value feature variable
        data['normalized_value'] = data.apply(lambda x: normalized_values(x.high, x.low, x.close), axis=1)
        print(data)
        # Add in the 4 regression variables
        data = n_day_regression(data, np.arange(0, len(data)))
        print(data)

        data = data[['volume', 'normalized_value', '3_reg', '5_reg', '10_reg', '20_reg']]
        print(data)

        data = data.dropna(axis=0)
        print(data)

        features_data = data.copy(deep=True)
        print(data)

        feature = scaler.transform(features_data[-1:].values)
        print(feature)


if __name__ == '__main__':
    unittest.main()
