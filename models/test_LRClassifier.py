from sklearn.datasets import make_classification

from models import LRClassifier


def test_multiclass():
    X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, n_classes=3,
                               random_state=1)
    print(X)
    print(y)
    classifier = Classifier.LR_MultiClassClassifier(X, y)
    row = [1.89149379, -0.39847585, 1.63856893, 0.01647165, 1.51892395, -3.52651223, 1.80998823, 0.58810926,
           -0.02542177, -0.52835426]
    yhat = classifier.predict_probability([row])
    print(f'Predicted Probabilities: {yhat[0]}')
