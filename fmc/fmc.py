import copy
from animate import make_video
from draw_state import draw_state
from puzzle_state import PuzzleState
from algorithm import Algorithm
import solver
from solver import SolverRunType
import scrambler
from database import db
from prettytable import PrettyTable
from fmc.round import FMCRound
import helper.discord as dh

class FMC:
    def __init__(self, bot, channel_id, duration, align_time=None, results_channel_id=None, ping_role=None,
                 warnings=None, warning_messages=None, repeating=False, size=4):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.duration = duration
        self.align_time = align_time
        self.warnings = warnings
        self.warning_messages = warning_messages
        self.repeating = repeating
        self.size = size

        if results_channel_id is None:
            self.results_channel = None
        else:
            self.results_channel = bot.get_channel(results_channel_id)

        if ping_role is None:
            self.role = None
        else:
            self.role = ping_role

        self.db_path = f"{self.channel.guild.id}/fmc/{self.channel.id}/"
        self.block_size = 100

        async def on_close(round_dict):
            await self.finish(round_dict)

            # if repeating, start a new round and set the timestamp so that it lines up
            # exactly with the start of the previous round + the duration
            if self.repeating:
                await self.start()
                timestamp = round_dict["timestamp"]
                db[self.round.db_path + "start_time"] = timestamp + self.round.duration

        async def on_warning(warning):
            index = self.warnings.index(warning)
            await self.channel.send(self.warning_messages[index])

        def generate():
            return scrambler.getScramble(size)

        def solve(pos):
            if size in [3, 4]:
                return solver.solve(pos, SolverRunType.ONE)
            return None

        self.round = FMCRound(self.db_path,
            duration=duration,
            align_time=align_time,
            warnings=warnings,
            on_close=on_close,
            on_warning=on_warning,
            generator=generate,
            solver=solve
        )

        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

    def round_number(self):
        return db[self.db_path + "round_number"]

    async def start(self):
        if self.round.running():
            return

        await self.channel.send("Starting FMC, please wait!")

        self.round.open()

        scramble = self.round.get_scramble()
        solution = self.round.get_solution()

        msg  = f"FMC scramble: {scramble}\n"
        if solution is not None:
            msg += f"Optimal solution length: {len(solution)}\n"
        msg +=  "Use **!submit** command to submit solutions (You can submit multiple times!), for example:\n"
        msg +=  "!submit LUR2DL2URU2LDR2DLUR2D2LU3RD3LULU2RDLDR2ULDLURUL2"

        # currently only have draw_state for 4x4
        if self.size == 4:
            img = draw_state(scramble)
            await dh.send_image(img, "scramble.png", msg, self.channel)
        else:
            await self.channel.send(msg)

        if self.role is not None:
            await self.channel.send(f"<@&{self.role}>")

    async def finish(self, round_dict):
        opt_known = round_dict["solution"] is not None

        results = round_dict["results"]
        scramble = round_dict["scramble"]
        if opt_known:
            optSolution = round_dict["solution"]
            optLength = len(optSolution)

        db[self.db_path + "round_number"] += 1

        # store the round in a block
        round_num = self.round_number()
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        # get the block and add the round to it
        block_path = self.db_path + f"history/round_blocks/{block}"
        if block_round == 0:
            block_dict = {}
        else:
            block_dict = db[block_path]

        # same as round_dict, but we convert the puzzle states and algorithms to strings
        round_dict2 = copy.deepcopy(round_dict)
        round_dict2["scramble"] = str(round_dict2["scramble"])
        round_dict2["solution"] = str(round_dict2["solution"])
        for id in round_dict2["results"]:
            round_dict2["results"][id] = str(round_dict2["results"][id])

        block_dict[block_round] = round_dict2
        db[block_path] = block_dict

        msg  =  "FMC results\n"
        msg += f"Scramble: {scramble}\n"
        if opt_known:
            msg += f"Optimal solution [{optLength}]: {optSolution}"

        if len(results) == 0:
            msg += "\n\nNo one joined :("
            await self.channel.send(msg)
        else:
            table = PrettyTable()
            if opt_known:
                table.field_names = ["Username", "Moves", "To optimal", "Solution"]
            else:
                table.field_names = ["Username", "Moves", "Solution"]

            # organise results in an array
            for (id, solution) in results.items():
                user = self.bot.get_user(id)
                if user:
                    length = len(solution)
                    if opt_known:
                        table.add_row([user.name, length, length - optLength, str(solution)])
                    else:
                        table.add_row([user.name, length, str(solution)])

            await dh.send_as_file(table.get_string(), "results.txt", msg, self.channel)
            if self.results_channel is not None:
                await dh.send_as_file(table.get_string(), "results.txt", msg, self.results_channel)

        if opt_known and self.size == 4:
            make_video(scramble, optSolution, 8)
            await dh.send_binary_file("movie.webm", "", self.channel)

    async def submit(self, user, solution):
        id = user.id
        name = user.name

        # simplify the solution before submitting
        solution.simplify()

        # check if the user has already submitted a solution
        if self.round.has_result(id):
            previous_length = len(self.round.result(id))
        else:
            previous_length = None
        new_length = len(solution)

        # submit the new solution
        self.round.submit(id, solution)

        # send message
        if previous_length is None:
            await self.channel.send(f"[{new_length}] Solution added for {name}")
        else:
            if new_length < previous_length:
                await self.channel.send(f"[{previous_length} -> {new_length}] Solution updated for {name}")
            else:
                await self.channel.send(f"[{new_length}] You already have a {previous_length} move solution, {name}")

    # given a scramble, find the round number that had it
    def find_scramble(self, scramble: PuzzleState):
        keys = db.prefix(self.db_path + "history/round_blocks/")
        for key in keys:
            block_num = int(key.split("/")[-1])
            block = db[key]
            for j in range(self.block_size):
                r = block[j]
                round_scramble = PuzzleState(r["scramble"])
                if round_scramble == scramble:
                    return self.block_size * block_num + j
        raise Exception("scramble not found")

    # delete a users historical result
    def delete_result(self, round_num, user):
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        key = self.db_path + f"history/round_blocks/{block}"
        b = db[key]
        del b[block_round]["results"][user]
        db[key] = b
