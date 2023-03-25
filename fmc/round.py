from log import log
import solver
from solver import SolverRunType
import scrambler
import time
from puzzle_state import PuzzleState
from algorithm import Algorithm
from discord.ext import tasks
from database import db

class FMCRound:
    def __init__(self, db_path, scramble=None, duration=86400, align_time=None, warnings=[],
                 on_close=None, on_warning=None,
                 generator=lambda: scrambler.getScramble(4),
                 solver=lambda x: solver.solve(x, SolverRunType.ONE)):
        self.db_path = db_path + "current/"
        self.scramble = scramble
        self.duration = duration
        # always make the start time in utc = align_time mod duration
        self.align_time = align_time
        self.warnings = warnings
        self.on_close = on_close
        self.on_warning  = on_warning
        self.generator = generator
        self.solver = solver

        self.loop.start()

    def running(self):
        return self.db_path + "start_time" in db

    def get_scramble(self):
        return PuzzleState(db[self.db_path + "scramble"])

    def get_solution(self):
        alg = db[self.db_path + "solution"]
        if alg == "None":
            return None
        return Algorithm(alg)

    def set_solution(self, alg):
        if self.solution_known():
            raise ValueError("solution is already known")

        scramble = self.get_scramble()
        scramble.apply(alg)
        if not scramble.solved():
            raise ValueError(f"solution does not solve scramble")

        db[self.db_path + "solution"] = str(alg)

    def solution_known(self):
        return db[self.db_path + "solution"] != "None"

    def elapsed(self):
        return int(time.time()) - int(db[self.db_path + "start_time"])

    def remaining(self):
        return max(0, self.duration - self.elapsed())

    def has_result(self, id):
        return self.db_path + f"results/{id}" in db

    def result(self, id):
        key = self.db_path + f"results/{id}"
        if key in db:
            return Algorithm(db[key])
        else:
            raise ValueError(f"user id {id} has not submitted a solution")

    def results(self):
        ids = [int(x.split("/")[-1]) for x in db.prefix(self.db_path + "results/")]

        results = {}
        for id in ids:
            results[id] = self.result(id)

        sorted_results = dict(sorted(results.items(), key=lambda x: len(x[1])))

        return sorted_results

    def open(self):
        if self.running():
            return

        log.info("opening fmc round")

        if self.scramble is None:
            scramble = self.generator()
            log.info(f"generated scramble: {scramble}")
        else:
            scramble = self.scramble
            log.info(f"using given scramble: {scramble}")

        # we may not be able to solve the position (e.g. big puzzles)
        # in which case the solver function should return None
        solution = self.solver(scramble)
        if solution is not None:
            log.info(f"found solution [{len(solution)}]: {solution}")

        db[self.db_path + "scramble"] = str(scramble)
        db[self.db_path + "solution"] = str(solution)
        start_time = int(time.time())
        if self.align_time is not None:
            start_time = (start_time // self.duration) * self.duration + self.align_time
        db[self.db_path + "start_time"] = start_time

        # initialize warning db entries
        for warning in self.warnings:
            db[self.db_path + f"warnings/{warning}"] = False

    def close(self):
        if not self.running():
            return

        log.info("closing fmc round")

        scramble = self.get_scramble()
        solution = self.get_solution()
        timestamp = db[self.db_path + "start_time"]
        results = self.results()

        # clean up db
        for x in db.prefix(self.db_path):
            del db[x]

        return {
            "scramble"  : scramble,
            "solution"  : solution,
            "timestamp" : timestamp,
            "results"   : results
        }

    def submit(self, user_id, solution):
        if not self.running():
            return

        log.info(f"user id {user_id} is submitting [{len(solution)}] {solution}")

        # check that the solution works
        scramble = self.get_scramble()
        scramble.apply(solution)
        if not scramble.solved():
            log.info("solution is invalid")

            # scramble has been modified, so get a new copy of the scramble from the db to print
            scramble = self.get_scramble()
            raise ValueError(f"solution does not solve scramble \"{scramble}\"")

        # add the new result if it's better than any previous result
        result_key = self.db_path + f"results/{user_id}"
        if result_key in db:
            old = self.result(user_id)
            if len(solution) < len(old):
                db[result_key] = str(solution)
        else:
            db[result_key] = str(solution)

        log.info("solution added")

    @tasks.loop(seconds=10)
    async def loop(self):
        if not self.running():
            return

        elapsed = self.elapsed()

        # check for any time warnings that need to be emitted
        if self.on_warning is not None:
            for warning in self.warnings:
                key = self.db_path + f"warnings/{warning}"
                if elapsed >= warning and not db[key]:
                    db[key] = True
                    log.info(f"emitting warning message for time={warning}")
                    await self.on_warning(warning)

        if elapsed >= self.duration:
            round_dict = self.close()
            if self.on_close is not None:
                log.info("emitting close message")
                await self.on_close(round_dict)
