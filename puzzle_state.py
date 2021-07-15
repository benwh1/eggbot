import math
import move
from move import Move
from algorithm import Algorithm

class PuzzleState:
    def __init__(self, state=None):
        if state == None:
            return

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

    def reset(self, w, h):
        arr = list(range(1, w*h)) + [0]
        self.arr = [arr[w*i : w*(i+1)] for i in range(h)]

    def width(self):
        return len(self.arr[0])

    def height(self):
        return len(self.arr)

    def size(self):
        return self.width(), self.height()

    def solved(self):
        w, h = self.size()
        return [x for row in self.arr for x in row] == list(range(1, w*h)) + [0]

    def blankPos(self):
        pos = [x == 0 for row in self.arr for x in row].index(True)
        w = self.width()
        return pos%w, pos//w

    def move(self, m):
        x, y = self.blankPos()
        w, h = self.size()
        good = False
        if m == Move.U:
            if y < h-1:
                self.arr[y][x], self.arr[y+1][x] = self.arr[y+1][x], self.arr[y][x]
                good = True
        elif m == Move.L:
            if x < w-1:
                self.arr[y][x], self.arr[y][x+1] = self.arr[y][x+1], self.arr[y][x]
                good = True
        elif m == Move.D:
            if y > 0:
                self.arr[y][x], self.arr[y-1][x] = self.arr[y-1][x], self.arr[y][x]
                good = True
        elif m == Move.R:
            if x > 0:
                self.arr[y][x], self.arr[y][x-1] = self.arr[y][x-1], self.arr[y][x]
                good = True

        if not good:
            raise ValueError(f"move \"{move.to_string(m)}\" can not be applied to puzzle state \"{self.to_string()}\"")

    def apply(self, alg):
        # create a copy so that self.arr isn't partially modified if we try and apply an alg that doesn't work
        copy = self
        try:
            for (direction, amount) in alg.moves:
                for i in range(amount):
                    copy.move(direction)
            self.arr = copy.arr
        except ValueError as e:
            raise ValueError(f"algorithm \"{alg.to_string()}\" can not be applied to puzzle state \"{self.to_string()}\"")

    def to_string(self):
        return "/".join([" ".join([str(x) for x in row]) for row in self.arr])
