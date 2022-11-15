import pandas as pd
import pytest
import pickle
from models import LinearModel

#@pytest.fixture
#def dataset_test():
#    with open('histoday_BTCUSD_Gemini.pkl', 'rb') as f:
#        dataset = pickle.load(f)
#    return dataset

@pytest.fixture
def model():
    with open('histoday_BTCUSD_Gemini.pkl', 'rb') as f:
        dataset = pickle.load(f)
    return LinearModel.LinearModel(dataset=dataset, training_end='2021-01-25')


def test_classifier(model):
    print(model.predict_test)
    model.show_confusion_matrix()
    model.compare()
    model.threshold = 0.99
    print(model.predict_test)
    model.show_confusion_matrix()
    model.compare()
