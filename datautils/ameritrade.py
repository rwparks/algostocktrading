import logging
from logging import Logger
import time
import calendar
from dataclasses import dataclass, field

import pandas as pd
import requests

api_key = 'DG5CSVD3ABJZSDWLLBSBUD0OSHDYNVH4'
ENDPOINT = 'https://api.tdameritrade.com/v1/marketdata/{stock_ticker}/pricehistory'


@dataclass
class Ameritrade:
    logger: Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    #@staticmethod
    def retrieve(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        start_date_ms = calendar.timegm(time.strptime(start_date, '%Y%m%d')) * 1000
        end_date_ms = calendar.timegm(time.strptime(end_date, '%Y%m%d')) * 1000
        payload = {'apikey': api_key, 'startDate': start_date_ms, 'endDate': end_date_ms,
                   'periodType': 'year', 'frequencyType': 'daily', 'frequency': '1',
                   'needExtendedHoursData': 'False'}
        response = requests.get(url=ENDPOINT.format(stock_ticker=ticker), params=payload)
        df = pd.DataFrame(data=response.json()['candles'])
        if not df.empty:
            df['time'] = pd.to_datetime(df['datetime'], unit='ms')
            df.set_index('time', inplace=True)
            return df.drop(columns=["datetime"])

        self.logger.warning(f'no historical data found for {ticker}')
        return df
