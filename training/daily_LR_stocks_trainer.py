import logging.config
import random
from typing import List
import click as click
import pandas as pd

from datautils.ameritrade import Ameritrade
from datautils.historical_data_fetcher import HistoricalDataFetcher
from datautils.historical_data_provider import HistoricalDataProvider
from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider
from features.features import features_for_training
from models.LinearModel import LinearModel

logging.config.fileConfig('training.logconf')
logger = logging.getLogger('training')

historical_data_provider: HistoricalDataProvider = Ameritrade()
persistence_provider: PersistenceProvider = ObjectSerialization('./data')
historical_data_fetcher = HistoricalDataFetcher(data_provider=historical_data_provider,
                                                persistence_provider=persistence_provider)


def get_best_scores(stocks: List, start_date: str, end_date: str, quantity: int) -> List:
    scores = []
    for ticker in stocks:
        try:
            dataset = historical_data_fetcher.fetch(ticker=ticker, start_date=start_date, end_date=end_date)
            if not dataset.empty:
                dataset.reset_index(inplace=True)
                dataset.rename(columns={'time': 'date'}, inplace=True)
                features = features_for_training(dataset, 10)
                trainer = LinearModel(features=features)
                trainer.threshold = 0.98
                scores.append((ticker, trainer.score))
        except KeyError:
            pass

    logger.debug(f'scores: {scores}')
    scores_filtered = filter(lambda score: score[1] == 1.0, scores)
    scores_list = list(scores_filtered).copy()
    logger.debug(f'scores filtered: {scores_list}')
    random.shuffle(scores_list)
    logger.debug(f'scores shuffled: {scores_list}')
    return [score[0] for score in scores_list]


@click.command()
@click.option('--sp500-file', '-s', required=False, type=str,
              default='sp500.lst', show_default=True, help='File of SP500 symbols')
@click.option('--dow-file', '-d', required=False, type=str,
              default='dow.lst', show_default=True, help='File of DOW symbols')
@click.option('--start-date', '-S', required=True, type=str, help='Start date in YYYYMMDD format')
@click.option('--end-date', '-E', required=True, type=str, help='End date in YYYYMMDD format')
@click.option('--classifier-file', required=True, type=str,
              help='Classifier file base name. The resulting file have the .clfr extension')
@click.option('--scalar-file', required=True, type=str,
              help='Scalar file base name. The resulting file have the .sclr extension')
@click.option('--quantity', '-q', required=False, default=20, show_default=True, type=int,
              help='The number symbols to build the classifier')
@click.option('--best-scores-file', '-B', required=False, default='best_scores.lst', show_default=True, type=str,
              help='The name of the best scores file')
def main(sp500_file: str, dow_file: str, start_date: str, end_date: str,
         classifier_file: str, scalar_file: str, quantity: int, best_scores_file: str) -> None:

    logger.debug(msg='a debug message')

    with open(sp500_file, 'r+') as f:
        sp500 = f.read().splitlines()
    with open(dow_file, 'r+') as f:
        dow = f.read().splitlines()

    best_scores = get_best_scores(stocks=sp500 + dow, start_date=start_date, end_date=end_date, quantity=quantity)
    with open(best_scores_file, 'w+') as f:
        for score in best_scores:
            print(score, file=f)

    features = pd.DataFrame()
    for ticker in best_scores[:quantity]:
        logger.info(f'retrieving {ticker} data')
        try:
            dataset = historical_data_fetcher.fetch(ticker=ticker, start_date=start_date, end_date=end_date)
            if not dataset.empty:
                dataset.reset_index(inplace=True)
                dataset.rename(columns={'time': 'date'}, inplace=True)
                features = pd.concat([features, features_for_training(dataset, 10)])
        except KeyError:
            pass

    #print(features)

    trainer = LinearModel(features=features)
    trainer.threshold = 0.98

    print(trainer.predict_test)
    #trainer.show_confusion_matrix()
    #trainer.compare()
    print(trainer.score)

    trainer.save_classifier(name=classifier_file)
    trainer.save_scaler(name=scalar_file)


if __name__ == '__main__':
    main()
