import pandas as pd
import pytest
import pickle
# import responses

from features import features_for_training_3class

pd.set_option('display.max_rows', None)


@pytest.fixture
def dataset_test():
    with open('dataset_test.pkl', 'rb') as f:
        dataset = pickle.load(f)
    return dataset


#def test_features_for_training_3class(dataset_test):
#    with open('test_features_for_training_3class__expected.pkl', 'rb') as f:
#        expected_df = pickle.load(f)
#
#    df = features_for_training_3class(dataset_test, 10)
#    assert df.equals(expected_df)
