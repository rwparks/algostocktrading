from collections import UserDict


class PredictionBucket(UserDict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sorted_get(self, i: int = 0) -> str:
        return sorted(self.data.items(), key=lambda e: e[1].probability, reverse=True)[i][0]

    #def has_key(self, ticker):
    #    return self.data.
    #def contains(self, ticker):
    #    return self.data.__contains__(ticker)
