import collections
from datetime import datetime
from typing import Protocol


class Prediction(collections.namedtuple("Prediction", "label probability")):
    pass


class PredictionProvider(Protocol):

    #def predict(self, ticker) -> Prediction:
    def predict(self, ticker, end_date: datetime) -> Prediction:
        """ Calculate prediction on ticker """


#class PredictionProviderConcrete:
#
#    def predict(self, ticker) -> Prediction:
#        """ Calculate prediction on ticker """
