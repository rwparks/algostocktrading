from operator import itemgetter

import numpy as np
import pandas as pd

from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.historical_data_provider import HistoricalDataProvider
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider
from features.features import features_for_training
from models.LinearModel import LinearModel

historical_data_provider: HistoricalDataProvider = Ameritrade()
persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                persistence_provider=persistence_provider)

# to get sp500 list: curl -L https://datahub.io/core/s-and-p-500-companies/r/0.csv
#with open('sp500.lst', 'r+') as f:
with open('sp500_20.lst', 'r+') as f:
    sp500 = f.read().splitlines()
with open('dow.lst', 'r+') as f:
    dow = f.read().splitlines()
#print('ticker,score')
#for ticker in stocks:
#for ticker in ['AAPL']:
scores = []
for ticker in sp500:
    try:
        dataset = historical_data_fetcher.fetch(ticker=ticker, start_date="20070101", end_date="20201231")
        dataset.reset_index(inplace=True)
        dataset.rename(columns={'time': 'date'}, inplace=True)
        features = features_for_training(dataset, 10)
        trainer = LinearModel(features=features)
        trainer.threshold = 0.98
        #print(f'{ticker},{trainer.score}')
        scores.append((ticker, trainer.score))
    except KeyError:
        pass

scores_sorted = sorted(scores, key=itemgetter(1), reverse=True)[0:10]
print(scores_sorted)

best_scores = [score[0] for score in scores_sorted]
print(best_scores)