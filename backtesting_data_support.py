from dataclasses import dataclass

import pandas as pd

from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.persistence_provider import PersistenceProvider, PersistenceProviderError


@dataclass
class BacktestingDataSupport:
    start_date: str
    end_date: str
    data_fetcher: HistoricalDataFetcher
    persistence_provider: PersistenceProvider
    day_close_format: str = 'day_{ticker}_close.pkl'
    day_list_format: str = 'day_list.pkl'

    @property
    def day_list(self):
        try:
            return self.persistence_provider.load(file_name_format=self.day_list_format)
        except PersistenceProviderError as e:
            print(e.message)

        data = self.data_fetcher.fetch(ticker='AAPL', start_date=self.start_date,
                                       end_date=self.end_date, persist=False)
        day_list = [day for day in data.index[1:]]
        self.persistence_provider.save(data=day_list, file_name_format=self.day_list_format)
        return day_list

    def close_series(self, ticker: str):
        try:
            return self.persistence_provider.load(ticker=ticker, file_name_format=self.day_close_format)
        except PersistenceProviderError as e:
            print(e.message)

        data = self.data_fetcher.fetch(ticker=ticker, start_date=self.start_date,
                                       end_date=self.end_date, persist=False)
        if not data.empty:
            close_series = data['close'].shift(1).dropna()
            self.persistence_provider.save(data=close_series, file_name_format=self.day_close_format, ticker=ticker)
            return close_series
        else:
            return pd.Series([])
