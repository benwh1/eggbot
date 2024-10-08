import copy
import math
import move
from move import Move

class PuzzleState:
    def __init__(self, state=None):
        if state == None:
            return

        state = state.strip()
        state = state.replace("\n", "/")
        arr = [row.split() for row in state.split("/")]
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

        # don't allow 1xN puzzles (Nx1 is not possible because we reshape them into squares)
        if len(arr[0]) == 1:
            raise ValueError(f"puzzle state \"{state}\" must have width greater than 1")

        self.arr = arr

    def __eq__(self, other):
        return self.arr == other.arr

    def reset(self, w, h=None):
        # if only one parameter given, assume square
        if h is None:
            h = w

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
            raise ValueError(f"move \"{move.to_string(m)}\" can not be applied to puzzle state \"{self}\"")

    def undo_move(self, m):
        self.move(move.inverse(m))

    def apply(self, alg):
        # create a copy so that self.arr isn't partially modified if we try and apply an alg that doesn't work
        p = copy.deepcopy(self)
        try:
            for (direction, amount) in alg.moves:
                for i in range(amount):
                    p.move(direction)
            self.arr = p.arr
        except ValueError as e:
            raise ValueError(f"algorithm \"{alg}\" can not be applied to puzzle state \"{self}\"")

    def __str__(self):
        return "/".join([" ".join([str(x) for x in row]) for row in self.arr])

    def solvable(self):
        # create a copy to avoid modifying self
        p = copy.deepcopy(self)

        w, h = p.size()
        gx, gy = p.blankPos()

        # move blank to bottom right
        for i in range(w-gx-1):
            p.move(Move.L)
        for i in range(h-gy-1):
            p.move(Move.U)

        # count transpositions required to bring the puzzle to solved
        swaps = 0
        for y in range(h):
            for x in range(w):
                if x == w-1 and y == h-1:
                    break

                # fix the cycle starting with the piece at (x, y)
                while p.arr[y][x] != 1+w*y+x:
                    # calculate where the tile at (x, y) belongs
                    t = p.arr[y][x]
                    tx, ty = (t-1)%w, (t-1)//w

                    # swap it into place
                    p.arr[y][x], p.arr[ty][tx] = p.arr[ty][tx], p.arr[y][x]
                    swaps += 1

        return swaps % 2 == 0

    def transpose(self):
        (w, h) = self.size()
        arr = [[0]*h for _ in range(w)]

        for y in range(h):
            for x in range(w):
                piece = self.arr[y][x]
                if piece == 0:
                    piece = w*h
                px, py = (piece-1)%w, (piece-1)//w

                new_piece = 1+py+h*px
                if new_piece == w*h:
                    new_piece = 0
                arr[x][y] = new_piece

        p = PuzzleState()
        p.reset(h, w)
        p.arr = arr

        return p
