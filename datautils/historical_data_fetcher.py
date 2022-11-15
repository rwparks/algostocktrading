import logging
from logging import Logger
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

from datautils.historical_data_provider import HistoricalDataProvider
from datautils.persistence_provider import PersistenceProvider, PersistenceProviderError
#from setup_logger import logger


@dataclass
class HistoricalDataFetcher:
    data_provider: HistoricalDataProvider
    day_hist_format: str = 'day_{ticker}.pkl'
    persistence_provider: Optional[PersistenceProvider] = None
    refresh: bool = False
    logger: Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def _retrieve(self, ticker: str, start_date: str, end_date: str, persist: bool) -> pd.DataFrame:
        self.logger.debug(f'retrieving {ticker} data')
        data = self.data_provider.retrieve(ticker=ticker, start_date=start_date, end_date=end_date)
        # self.logger.debug(data)
        if persist and self.persistence_provider is not None and not data.empty:
            self.logger.debug(f'saving {ticker} data')
            self.persistence_provider.save(data=data, file_name_format=self.day_hist_format, ticker=ticker)
        return data

    def fetch(self, ticker: str, start_date: str, end_date: str, persist: bool = True) -> pd.DataFrame:
        if persist and self.persistence_provider is not None and not self.refresh:
            try:
                return self.persistence_provider.load(ticker=ticker, file_name_format=self.day_hist_format)
            except PersistenceProviderError as e:
                self.logger.error(e.message)

        return self._retrieve(ticker=ticker, start_date=start_date, end_date=end_date, persist=persist)

