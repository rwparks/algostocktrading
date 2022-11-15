from typing import Protocol

import pandas as pd


class HistoricalDataProvider(Protocol):

    def retrieve(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """ retrieve data from the historical data provider """
