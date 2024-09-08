from enum import Enum
from log import log
import subprocess
import os
from algorithm import Algorithm
import solver_5x5

class SolverRunType(Enum):
    ONE = "one"
    ALL = "all"
    GOOD = "good"

class Solver:
    def __init__(self, w, h, keep_alive=False):
        self.width = w
        self.height = h
        self.name = f"solver{w}x{h}"
        self.running = False
        self.keep_alive = keep_alive

    def start(self):
        program = f"./solvers/{self.name}"
        log.info(f"starting solver \"{program}\"")
        self.process = subprocess.Popen(program, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.running = True

    def stop(self):
        log.info(f"terminating {self.name}")
        self.process.terminate()
        self.running = False

    def solve(self, scramble, mode):
        # check that the scramble is solvable
        if not scramble.solvable():
            raise ValueError(f"puzzle state \"{scramble}\" is not solvable")

        if not self.running:
            self.start()

        self.process.stdin.write(mode.value + "\n")
        log.info(f"set solver to mode \"{mode.value}\"")

        log.info(f"solving scramble: {scramble}")

        self.process.stdin.write(f"{scramble}\n")
        self.process.stdin.flush()

        solutions = []
        while True:
            line = self.process.stdout.readline().strip()
            if line == "done":
                break
            else:
                solution = Algorithm(line)
                solutions.append(solution)
                log.info(f"found solution: {solution}")

        # kill the solver process if we don't want to keep it running
        if not self.keep_alive:
            self.stop()

        log.info(f"solver finished, found {len(solutions)} solutions")
        return solutions

    def solveOne(self, scramble):
        return self.solve(scramble, mode=SolverRunType.ONE)[0]

    def solveGood(self, scramble):
        return self.solve(scramble, mode=SolverRunType.GOOD)

    def solveAll(self, scramble):
        return self.solve(scramble, mode=SolverRunType.ALL)

solvers = {
    (2, 2): Solver(2, 2, keep_alive=True),
    (3, 2): Solver(3, 2, keep_alive=True),
    (4, 2): Solver(4, 2, keep_alive=True),
    (5, 2): Solver(5, 2, keep_alive=True),
    (6, 2): Solver(6, 2, keep_alive=True),
    (7, 2): Solver(7, 2, keep_alive=True),
    (8, 2): Solver(8, 2, keep_alive=True),
    (3, 3): Solver(3, 3, keep_alive=True),
    (4, 3): Solver(4, 3, keep_alive=True),
    (5, 3): Solver(5, 3, keep_alive=True),
    (4, 4): Solver(4, 4, keep_alive=True)
}

def solve(puzzle, mode):
    (w, h) = puzzle.size()
    if (w, h) in solvers:
        solver = solvers[(w, h)]
        solutions = solver.solve(puzzle, mode)
        if mode == SolverRunType.ONE:
            return solutions[0]
        else:
            return solutions
    elif (h, w) in solvers:
        solver = solvers[(h, w)]
        p = puzzle.transpose()
        solutions = solver.solve(p, mode)
        transposed_sols = [s.transpose() for s in solutions]
        transposed_sols.sort(key=lambda s: [move.value for (move, amount) in s.moves for _ in range(amount)])
        if mode == SolverRunType.ONE:
            return transposed_sols[0]
        else:
            return transposed_sols
    elif (w, h) == (5, 5):
        if mode != SolverRunType.ONE:
            raise ValueError("5x5 solver only supports one solution")
        return solver_5x5.solve(puzzle)
    else:
        raise Exception(f"{w}x{h} solver not available")
