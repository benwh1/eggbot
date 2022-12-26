import numpy as np
from numpy.polynomial.polynomial import polypow, polymul
from probability.comparison import Comparison

# represents a discrete probability distribution on the points 0, 1, ..., n
class Distribution:
    def __init__(self, arr):
        total = sum(arr)
        self.n = len(arr)-1
        self.arr = np.array([x/total for x in arr])

    def __add__(self, other):
        return Distribution(polymul(self.arr, other.arr))

    # sum of n iid copies of this distribution
    def sum_distribution(self, n):
        if n < 1:
            raise ValueError("number of copies of the distrbution must be at least 1")
        elif n == 1:
            return self
        return Distribution(polypow(self.arr, n))

    def prob_range(self, start, end):
        if start < 0:
            start = 0
        if end > self.n:
            end = self.n

        if end < start:
            return 0
        if start == 0 and end == self.n:
            return 1

        return sum(self.arr[start:end+1])

    def prob(self, n, comp):
        if comp == Comparison.Null:
            return 0
        if comp == Comparison.All:
            return 1

        if comp == Comparison.LessThan:
            start = 0
            end = n-1
        elif comp == Comparison.Equal:
            start = n
            end = n
        elif comp == Comparison.GreaterThan:
            start = n+1
            end = self.n
        elif comp == Comparison.LessThanOrEqual:
            start = 0
            end = n
        elif comp == Comparison.GreaterThanOrEqual:
            start = n
            end = self.n
        elif comp == Comparison.NotEqual:
            return 1 - self.prob(n, Comparison.Equal)

        return self.prob_range(start, end)
