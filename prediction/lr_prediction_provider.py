from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from datautils.historical_data_fetcher import HistoricalDataFetcher
from features.features import features_for_production
from models.LRClassifier import LRClassifier

from prediction.prediction_provider import Prediction


@dataclass
class LRPredictionProvider:
    classifier: LRClassifier
    scaler: MinMaxScaler
    historical_data_fetcher: HistoricalDataFetcher
    #end_date: datetime = None
    # n: int = 25
    n: int = 40

    def _get_features_data(self, ticker: str, end_date: datetime) -> pd.DataFrame:
        # if not self.end_date:
        #    self.end_date = datetime.now()
        #start = self.end_date - timedelta(days=self.n)
        start = end_date - timedelta(days=self.n)
        #dataset = self.historical_data_fetcher.fetch(ticker=ticker,
        #                                             start_date=start.strftime('%Y%m%d'),
        #                                             end_date=self.end_date.strftime('%Y%m%d'))
        dataset = self.historical_data_fetcher.fetch(ticker=ticker,
                                                     start_date=start.strftime('%Y%m%d'),
                                                     end_date=end_date.strftime('%Y%m%d'))
        dataset.reset_index(inplace=True)
        return dataset

    # def predict(self, ticker) -> Prediction:
    def predict(self, ticker, end_date: datetime = datetime.now()) -> Prediction:
        # Grab the last row which will be the features for this day

        pd.set_option('display.max_columns', None, 'display.width', 160)
        # features_data = features_for_production(self._get_features_data(ticker).copy(deep=True))
        features_data = features_for_production(
            self._get_features_data(ticker=ticker, end_date=end_date).copy(deep=True))
        feature = self.scaler.transform(features_data[-1:].values)

        return Prediction(label=self.classifier.predict(feature, 0.9)[0],
                          probability=self.classifier.predict_probability(feature)[:, 0][0])
