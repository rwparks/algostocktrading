import numpy as np
from dataclasses import dataclass, field
from sklearn.linear_model import LogisticRegression

@dataclass
class LRClassifier:
    x: object
    y: np.int64
    estimator: LogisticRegression = field(default_factory=LogisticRegression)

    def __post_init__(self):
        #self.estimator.set_params(**{'random_state': 0})
        self.estimator.fit(self.x, self.y)

    @staticmethod
    def _threshold(X_proba: np.ndarray, threshold: float) -> np.array:
        """
        Inputs the probability and returns 1 or 0 based on the threshold
        Parameters
        ----------
        X_proba
        threshold

        Returns
        -------

        """
        return np.array([0 if x > threshold else 1 for x in X_proba[:, 0]])

    @property
    def classifier(self) -> LogisticRegression:
        """

        Returns
        -------

        """
        return self.estimator

    def predict(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        """
        Predict class labels for X.
        Parameters
        ----------
        X
        threshold

        Returns
        -------

        """
        if threshold is not None:
            return self._threshold(self.predict_probability(X), threshold)
        else:
            return self.estimator.predict(X)

    def predict_probability(self, X: np.ndarray) -> np.ndarray:
        """
        Return probability estimates for all classes
        Parameters
        ----------
        X

        Returns
        -------

        """
        return self.estimator.predict_proba(X)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """

        Parameters
        ----------
        X
        y

        Returns
        -------

        """
        return self.estimator.score(X, y)


@dataclass
class LR_MultiClassClassifier:
    x: object
    y: np.int64
    estimator: LogisticRegression = field(default_factory=LogisticRegression)

    def __post_init__(self):
        self.estimator.set_params(**{'multi_class': 'multinomial', 'solver': 'lbfgs'})
        self.estimator.fit(self.x, self.y)

    @property
    def classifier(self) -> LogisticRegression:
        return self.estimator

    def predict(self, x):
        return self.estimator.predict(x)

    def predict_probability(self, x):
        return self.estimator.predict_proba(x)

    def score(self, x, y):
        return self.estimator.score(x, y)
