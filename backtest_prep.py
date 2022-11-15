from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider, PersistenceProviderError

day_hist_format = 'day_{ticker}.pkl'
day_close_format = 'day_{ticker}_close.pkl'
day_list_format = 'day_list.pkl'


def get_day_list(fetcher: HistoricalDataFetcher, start_date: str, end_date: str):

    persistence_provider: PersistenceProvider = ObjectSerialization(file_name_format=day_list_format,
                                                                    persist_dir=persist_dir)

    try:
        return persistence_provider.load()
    except PersistenceProviderError as e:
        print(e.message)

    data = fetcher.fetch(ticker='AAPL', start_date=start_date, end_date=end_date)
    day_list = [day for day in data.index[1:]]
    persistence_provider.save(data=day_list)
    return day_list


def get_close_series(fetcher: HistoricalDataFetcher, ticker: str, start_date: str, end_date: str):

    persistence_provider: PersistenceProvider = ObjectSerialization(file_name_format=day_close_format,
                                                                    persist_dir=persist_dir)

    try:
        return persistence_provider.load(ticker=ticker)
    except PersistenceProviderError as e:
        print(e.message)

    close_series = fetcher.fetch(ticker=ticker, start_date=start_date, end_date=end_date)
    if not close_series.empty:
        persistence_provider.save(data=close_series['close'].shift(1).dropna(),
                                  ticker=ticker, start_date=start_date, end_date=end_date)

    return close_series


if __name__ == '__main__':
    start_date = '20200101'
    end_date = '20211231'
    persist_dir = f'./backtesting_data/{start_date}-{end_date}'
    data_fetcher: HistoricalDataFetcher = HistoricalDataFetcher(data_provider=Ameritrade(),
                                                                persistence_provider=ObjectSerialization(
                                                                    file_name_format=day_hist_format,
                                                                    persist_dir=persist_dir))

    day_list = get_day_list(fetcher=data_fetcher, start_date=start_date, end_date=end_date)

    aapl_close = get_close_series(fetcher=data_fetcher, ticker='AAPL', start_date=start_date, end_date=end_date)

    print(aapl_close[day_list[0]])

    #build_close_series(ticker='A', start_date=start_date, end_date=end_date)
