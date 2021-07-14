import math

class PuzzleState:
    def __init__(self, state):
        state = state.strip()
        state = state.replace("\n", "/")
        arr = [row.split(" ") for row in state.split("/")]
        arr = [[int(x) for x in row] for row in arr]

        # check that all numbers from 0 to len-1 appear once
        flatArr = [x for row in arr for x in row]
        flatArr.sort()
        if flatArr != list(range(len(flatArr))):
            raise ValueError(f"puzzle state \"{state}\" does not contain correct pieces")

        # if no row separators, check if the length is a square
        if len(arr) == 1:
            n = len(arr[0])
            sqrtn = int(math.sqrt(n)+0.5)
            if sqrtn**2 == n:
                # reshape the array into a square
                arr = [arr[0][sqrtn*i : sqrtn*(i+1)] for i in range(sqrtn)]
            else:
                # not a square, so we can't guess the size
                raise ValueError(f"puzzle state \"{state}\" is not a square (length = {n})")

        # check that all rows are the same length
        for row in arr:
            if len(row) != len(arr[0]):
                raise ValueError(f"puzzle state \"{state}\" has rows of differing lengths")

        self.arr = arr

    def width(self):
        return len(self.arr[0])

    def height(self):
        return len(self.arr)
