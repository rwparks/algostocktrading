from collections import namedtuple
from dataclasses import dataclass, field, InitVar

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class Xtype(namedtuple("Xtype", "raw scaled")):
    """Value type for X

    raw - not scaled

    scaled - scaled
    """
    pass


class Train(namedtuple("Train", "X y")):
    """Training X and y values

    X - the independent variables

    y - the dependent variables
    """
    pass


class Test(namedtuple("Test", "X y")):
    """Testing X and y values

    X - the independent variables

    y - the dependent variables
    """
    pass


@dataclass()
class DataPreprocessor:
    features: pd.DataFrame
    scale: InitVar[bool] = True
    #scale: InitVar[bool] = False
    #scaler: StandardScaler = field(init=False, default_factory=StandardScaler)
    scaler: MinMaxScaler = field(init=False, default_factory=MinMaxScaler)
    X_train: object = field(init=False)
    X_test: object = field(init=False)
    y_train: np.int64 = field(init=False)
    y_test: np.int64 = field(init=False)
    X_train_scaled: object = field(init=False, default=None)
    X_test_scaled: object = field(init=False, default=None)

    def __post_init__(self, scale):
        self.X_train, self.X_test, self.y_train, self.y_test = self._split()
        if scale:
            self.X_train_scaled, self.X_test_scaled = self._scale(c_start=2)

    @property
    def train(self) -> Train:
        """
        Get training independent and dependent variables

        Returns
        -------
        namedTuple
            The training independent and dependent variables

        """
        return Train(Xtype(self.X_train, self.X_train_scaled), self.y_train)

    @property
    def test(self) -> Test:
        """
        Get testing independent and dependent variables

        Returns
        -------
        namedTuple
            The testing independent and dependent variables

        """
        return Test(Xtype(self.X_test, self.X_test_scaled), self.y_test)

    def _split(self, r_start=None, r_end=None, c_start=None, c_end=None, dv_col=-1) -> list:

        """ Split the data into training and test datasets

        Parameters
        ----------
        r_start
            Starting row index for independent variables
        r_end
            Ending row index for independent variables
        c_start
            Starting column index for independent variables
        c_end
            Ending column index for independent variables
        dv_col
            Column index for dependent variable

        Returns
        -------
        list
            List containing train-test split of inputs

        """
        if dv_col == -1 and c_end is None:
            c_end = -1
        # start new
        self.features = self.features.sample(frac=1, random_state=3).reset_index(drop=True)
        self.features['target'] = self.features['target'].astype('category')
        # end new
        #print(self.features)
        X = self.features.iloc[r_start:r_end, c_start:c_end].values
        #X = self.scaler.fit_transform(self.features.iloc[r_start:r_end, c_start:c_end].values)
        #print(X)
        y = self.features.iloc[:, dv_col].values
        #return train_test_split(X, y, test_size=0.25, random_state=0)
        return train_test_split(X, y, test_size=0.05, random_state=50, shuffle=True)

    def _scale(self, r_start: int = None, r_end: int = None, c_start: int = None, c_end: int = None):
        """ Use the StandardScaler to fit_transform the training dataset and transform the testing dataset.

        Parameters
        ----------
        r_start
            Starting row index for independent variables
        r_end
            Ending row index for independent variables
        c_start
            Starting column index for independent variables
        c_end
            Ending column index for independent variables

        Returns
        -------
        (np.int64, np.int64)

        """
        X_train_scaled = self.scaler.fit_transform(self.train.X.raw[r_start:r_end, c_start:c_end])
        #X_train_scaled = self.train.X.raw[r_start:r_end, c_start:c_end]
        #print(X_train_scaled)
        X_test_scaled = self.scaler.transform(self.test.X.raw[r_start:r_end, c_start:c_end])
        return X_train_scaled, X_test_scaled
