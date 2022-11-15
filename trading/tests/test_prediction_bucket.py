import unittest

from prediction.prediction_provider import Prediction
from trading.prediction_bucket import PredictionBucket


class PredictionBucketTestCase(unittest.TestCase):

    @staticmethod
    def test_sorted():
        bucket = PredictionBucket()
        # bucket['d'] = 1
        bucket['A'] = Prediction(label=0, probability=95.0)
        bucket['B'] = Prediction(label=0, probability=94.0)
        bucket['C'] = Prediction(label=0, probability=96.0)
        assert 'A' in bucket
        assert bucket.sorted_get() == 'C'
        assert bucket.sorted_get(1) == 'A'
        assert bucket.sorted_get(2) == 'B'


if __name__ == '__main__':
    unittest.main()
