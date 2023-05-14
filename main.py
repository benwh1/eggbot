from dotenv import load_dotenv

load_dotenv()

import scrambler
import solver
from solver import SolverRunType
import os
from keep_alive import keep_alive
import discord
from discord.ext import commands,tasks
import html2text
import traceback
from log import log
from time import perf_counter
import math
import random
import numpy as np
import cv2
import sys
import requests
import re
import regex
import asyncio
import bot as bot_helper
from formatting import time as time_format
import move
import helper.serialize as serialize
import helper.discord as dh
import permissions
import config.channels
import config.emoji
import config.roles
import solve_db
from animate import make_video
from puzzle_state import PuzzleState
from algorithm import Algorithm
from analyse import analyse
from draw_state import draw_state
from fmc.fmc import FMC
from movesgame.movesgame import MovesGame
from movesgame.tournament import MovesGameTournament
from optimal_game.game import OptimalGame
from random_game import RandomGame
from probability import comparison, distributions
from probability.format import format_prob
from leaderboard import commands as lb_commands
from leaderboard import link
from database import db
import manhattan
import statistics

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

#_________________________probably for !paint
def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

def convertRgbToWeight(rgbArray):
    arrayWithPixelWeight = []
    for i in range(int(rgbArray.size / rgbArray[0].size)):
        for j in range(int(rgbArray[0].size / 3)):
            lum = 255 - (
                int(rgbArray[i][j][0])
                + int(rgbArray[i][j][1])
                + int(rgbArray[i][j][2]) / 3
            )  # Reversed luminosity
            arrayWithPixelWeight.append(lum / 255)  # Map values from range 0-255 to 0-1
    return arrayWithPixelWeight

# Update Leaderboard automatically every N minutes
@tasks.loop(minutes=120)
async def silent_update():
    lb_commands.update()

#____________________________discord started
@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")

    # check for message to send after a restart/update
    if "restart/channel_id" in db.keys() and "restart/message" in db.keys():
        channel_id = db["restart/channel_id"]
        channel = bot.get_channel(channel_id)
        message = db["restart/message"]
        if channel is not None:
            await channel.send(message)
        del db["restart/channel_id"]
        del db["restart/message"]

    # create fmc
    global daily_fmc, short_fmc
    daily_fmc = FMC(bot,
        channel_id=config.channels.daily_fmc,
        results_channel_id=config.channels.daily_fmc_results,
        duration=86400,
        align_time=0,
        ping_role=config.roles.fmc,
        warnings=[23*3600],
        warning_messages=["One hour remaining!"],
        repeating=True
    )
    short_fmc = FMC(bot,
        channel_id=config.channels.ten_minute_fmc,
        duration=600,
        warnings=[60*5, 60*9],
        warning_messages=["5 minutes remaining!", "One minute remaining!"]
    )
    fmc_5x5 = FMC(bot,
        channel_id=config.channels.fmc_5x5,
        duration=2*24*60*60,
        align_time=24*60*60, # just because we happened to start it on an odd-numbered date
        ping_role=config.roles.fmc,
        warnings=[24*60*60, 47*60*60],
        warning_messages=["One day remaining.", "One hour remaining!"],
        repeating=True,
        size=5
    )
    await daily_fmc.start()
    await fmc_5x5.start()

    # dict of fmc objects by id
    global fmcs
    fmcs = {x.channel.id : x for x in [daily_fmc, short_fmc, fmc_5x5]}

    # create movesgame
    global movesgame, movesgame_tournament
    movesgame = MovesGame(bot, config.channels.movesgame)
    movesgame_tournament = MovesGameTournament(bot, config.channels.movesgame_tournament)

    # create optimal_game
    global optimal_game
    optimal_game = OptimalGame(bot, config.channels.optimal_game)

    # create random games
    global random_games
    random_game = RandomGame(
        bot=bot,
        channel_ids=config.channels.random_game,
        game_id="egg",
        message=":egg: Egg! :egg:",
        response="egg",
        freq=181440
    )
    random_game.start()
    yaytso = f"<:yaytso:{config.emoji.yaytso}>"
    random_game_2 = RandomGame(
        bot=bot,
        channel_ids=config.channels.random_game,
        game_id="yaytso",
        message=f"{yaytso} Yaytso! {yaytso}",
        response="yaytso",
        freq=181440*25
    )
    random_game_2.start()
    random_games = {
        "egg"    : random_game,
        "yaytso" : random_game_2
    }

    # Start automatic leaderboard updates
    if os.environ["auto_update"] == "1":
        await asyncio.sleep(7200)
        silent_update.start()

@bot.listen()
async def on_message(message):
    if message.author.bot:
        return

    if "pls" in message.content.lower():
        await message.add_reaction("eff:803888415858098217")
    if bot.user in message.mentions:
        await message.channel.send("You are egg, " + message.author.mention)
    if "fuck you" in message.content.lower():
        await message.channel.send("no u, " + message.author.mention)
    if "scrable" in message.content.lower():
        await message.channel.send("Infinity tps, " + message.author.mention + "?")
        await message.add_reaction("0️⃣")
    if "egg" in message.content.lower():
        if random.randint(1, 100) == 1:
            if random.randint(1, 25) == 1:
                await message.channel.send("Eggggggggggggggggggg!")
                await message.add_reaction("🥚")
                for id in config.emoji.eggs:
                    await message.add_reaction(bot.get_emoji(id))
            else:
                await message.channel.send("Egg!")
                await message.add_reaction("🥚")
                for id in config.emoji.eggs[:3]:
                    await message.add_reaction(bot.get_emoji(id))

    # find the first line of the message containing a command
    lines = message.content.split("\n")
    command_lines = [line.strip() for line in lines if line.startswith("!")]
    if len(command_lines) == 0:
        return
    command = command_lines[0]

    log.info(f"found command from user {message.author}")
    log.info(f"command: {command}")

    if command.startswith("!fmc"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        msg  = f"Current FMC scramble: {fmc.round.get_scramble()}\n"
        if fmc.round.solution_known():
            msg += f"Optimal solution length: {len(fmc.round.get_solution())}\n"
        msg += "Time remaining: " + time_format.format_long(fmc.round.remaining())
        await message.channel.send(msg)
    elif command.startswith("!submit"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        try:
            await message.delete()

            # !submit [solution, optionally spoilered]
            solution_reg = regex.optionally_spoilered(regex.algorithm("solution"))
            reg = re.compile(f"!submit\s+{solution_reg}")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to read solution")

            groups = match.groupdict()

            solution = Algorithm(groups["solution"])
            await fmc.submit(message.author, solution)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!results"):
        # fmc results
        if message.channel.id in fmcs:
            fmc = fmcs[message.channel.id]
            if not fmc.round.running():
                return
            results = fmc.round.results()
            if len(results) == 0:
                msg = "No results yet"
            else:
                msg = ""
                for (id, result) in results.items():
                    user = bot.get_user(id)
                    if user:
                        msg += f"{user.name}: {len(result)}\n"
            await message.channel.send(msg)
        # movesgame results
        elif message.channel.id == movesgame.channel.id:
            results = movesgame.lifetime_results()
            ids = results.keys()

            # sort users by fraction of correct results
            fractions = {}
            for id in ids:
                good = results[id]["correct"]
                bad = results[id]["incorrect"]
                fractions[id] = good/(good+bad)
            sorted_ids = [x[0] for x in sorted(fractions.items(), key=lambda x: -x[1])]

            results_msg = ""
            provisional_msg = ""
            for id in sorted_ids:
                user = bot.get_user(id)
                if user:
                    good = results[id]["correct"]
                    bad = results[id]["incorrect"]
                    formatted = format(100*good/(good+bad), ".2f") + "%"

                    # only show results for people with enough rounds
                    if good+bad >= 30:
                        results_msg += f"{user.name}: {good}/{good+bad} = {formatted}\n"
                    else:
                        provisional_msg += f"({user.name}: {good}/{good+bad} = {formatted})\n"

            await message.channel.send(results_msg + provisional_msg)
        elif message.channel.id == optimal_game.channel.id:
            results = optimal_game.lifetime_results()
            ids = results.keys()

            fractions = {}
            for (id, result) in results.items():
                fractions[id] = result["distance"]/result["rounds"]
            sorted_ids = [x[0] for x in sorted(fractions.items(), key=lambda x: x[1])]

            results_msg = ""
            provisional_msg = ""
            for id in sorted_ids:
                user = bot.get_user(id)
                if user:
                    result = results[id]
                    distance = result["distance"]
                    rounds = result["rounds"]
                    formatted = format(fractions[id], ".4f")

                    # only show results for people with enough rounds
                    if rounds >= 30:
                        results_msg += f"{user.name}: {distance}/{rounds} = {formatted}\n"
                    else:
                        provisional_msg += f"({user.name}: {distance}/{rounds} = {formatted})\n"

            await message.channel.send(results_msg + provisional_msg)
    elif command.startswith("!deleteresult"):
        try:
            if not permissions.is_egg_admin(message.author):
                raise Exception("you don't have permission")

            games = dict(list(fmcs.items()) + [(movesgame.channel.id, movesgame), (optimal_game.channel.id, optimal_game)])
            game = games[message.channel.id]

            scramble_reg = regex.puzzle_state("scramble")
            reg = re.compile(f"!deleteresult(\s+{scramble_reg})(\s+(?P<user_id>[0-9]+))")
            match = reg.fullmatch(command)
            if match is None:
                raise SyntaxError(f"failed to parse args")
            groups = match.groupdict()

            scramble = PuzzleState(groups["scramble"])
            user_id = int(groups["user_id"])
            round_number = game.find_scramble(scramble)
            game.delete_result(round_number, user_id)

            await message.channel.send("Result deleted")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!setsolution"):
        if not permissions.is_egg_admin(message.author):
            return
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        try:
            await message.delete()

            solution_reg = regex.optionally_spoilered(regex.algorithm("solution"))
            reg = re.compile(f"!setsolution\s+{solution_reg}")
            match = reg.fullmatch(command)
            if match is None:
                raise SyntaxError(f"failed to read solution")
            groups = match.groupdict()
            solution = Algorithm(groups["solution"])

            fmc.round.set_solution(solution)
            await message.channel.send(f"Added solution. Length: {len(solution)} moves")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!numwrs"):
        if command == "!numwrs":
            url = "https://slidysim.com/leaderboard/records.html"
            msg = "WRs:"
        elif command == "!numwrs moves":
            url = "https://slidysim.com/leaderboard/records_moves.html"
            msg = "Movecount WRs:"

        text = requests.get(url, timeout=5).text
        lines = html2text.html2text(text).splitlines()
        idx = lines.index("---|---  ")
        lines = lines[idx+1:-3]
        msg += "\n```" + "\n".join(lines) + "```"
        msg = msg.replace(" |", ":")
        await message.channel.send(msg)
    elif command.startswith("!startfmc"):
        if message.channel.id != short_fmc.channel.id or short_fmc.round.running():
            return
        await short_fmc.start()
    elif command.startswith("!update"):
        await message.channel.send("Wait for it!")
        try:
            lb_commands.update()
            webpage = os.environ["webpage"]
            msg = f"Webpage updated!\n{webpage}"
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getreal"):
        await message.channel.send("Generating scramble!")

        state = scrambler.getScramble(4)
        solution = solver.solve(state, SolverRunType.ONE)
        scramble = Algorithm("D3 R U2 R D2 R U3 L3") + solution.inverse()

        scrambleState = PuzzleState()
        scrambleState.reset(4, 4)
        scrambleState.apply(scramble)

        img = draw_state(scrambleState)
        msg = str(scrambleState) + "\n" + str(scramble)
        await dh.send_image(img, "scramble.png", msg, message.channel)
    elif command.startswith("!getscramble"):
        contentArray = command.lower().split(" ")
        n = 4
        if len(contentArray)>1:
            n = int(contentArray[1])
        scramble = scrambler.getScramble(n)
        if n == 4:
            img = draw_state(scramble)
            msg = f"Your random 4x4 scramble: \n{scramble}"
            await dh.send_image(img, "scramble.png", msg, message.channel)
        else:
            await message.channel.send(f"Random scramble for {n}x{n} puzzle\n{scramble}")
    elif command.startswith("!getwr"):
        try:
            size_reg = regex.size("width", "height", "size")
            reg = re.compile(f"!getwr(\s+{size_reg})(\s+(?P<is_moves>moves))?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            if groups["is_moves"] is None:
                url = "https://slidysim.com/leaderboard/records_all.html"
            else:
                url = "https://slidysim.com/leaderboard/records_all_moves.html"

            text = requests.get(url, timeout=5).text
            records = html2text.html2text(text).splitlines()[8:]

            size = match["size"]
            matching = [s for s in records if size in s]

            if len(matching) == 0:
                await message.channel.send("Couldn't find any records")
            else:
                await message.channel.send(f"```{matching[0]}```")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!wrsby"):
        try:
            reg = re.compile("!wrsby(\s+(?P<user>[A-Za-z0-9]+))(\s+(?P<is_moves>moves))?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            moves = groups["is_moves"] is not None
            if moves:
                url = "https://slidysim.com/leaderboard/records_all_moves.html"
            else:
                url = "https://slidysim.com/leaderboard/records_all.html"

            text = requests.get(url, timeout=5).text
            records = html2text.html2text(text).splitlines()[8:]

            username = groups["user"]
            matching = [s for s in records if username in s]

            msg = "\n".join(matching)
            if len(matching) == 0:
                await message.channel.send("Couldn't find any records")
            else:
                if len(msg) > 1950:
                    if moves:
                        text = "Movecount WR list:"
                    else:
                        text = "WR list:"
                    await dh.send_as_file(msg, "wrsby.txt", text, message.channel)
                else:
                    await message.channel.send("```" + msg + "```")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getpb"):
        try:
            size_reg = regex.size("width", "height", "size")
            reg = re.compile(f"!getpb(\s+(?P<user>[A-Za-z0-9]+))??(\s+{size_reg})?(\s+(?P<pbtype>time|moves|tps))?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # if no username parameter is given, look up the message author's linked username
            if groups["user"] is None:
                user = link.get_leaderboard_user(message.author.id)
            else:
                user = groups["user"]

            # if no size given, check if we're in an NxN channel. if not, default to 4x4
            if groups["size"] is None:
                channel_id = message.channel.id
                if channel_id in config.channels.nxn_channels:
                    width = height = config.channels.nxn_channels[channel_id]
                else:
                    width = height = 4
            else:
                width = int(groups["width"])
                if groups["height"] is None:
                    height = width
                else:
                    height = int(groups["height"])

            if groups["pbtype"] is None:
                pbtype = "time"
            else:
                pbtype = groups["pbtype"]

            msg = lb_commands.get_pb(width, height, user, pbtype=pbtype)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getreq"):
        try:
            size_reg = regex.size("width", "height", "size")
            reg = re.compile(f"!getreq(\s+(?P<tier>[A-Za-z0-9]+))(\s+{size_reg})?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            tier = groups["tier"]

            # if no size given, check if we're in an NxN channel. if not, default to 4x4
            if groups["size"] is None:
                channel_id = message.channel.id
                if channel_id in config.channels.nxn_channels:
                    width = height = config.channels.nxn_channels[channel_id]
                else:
                    width = height = 4
            else:
                width = int(groups["width"])
                if groups["height"] is None:
                    height = width
                else:
                    height = int(groups["height"])

            msg = lb_commands.get_req(width, height, tier)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!animate"):
        try:
            # !animate [optional scramble] [solution] [optional tps]
            scr_reg = regex.puzzle_state("scramble")
            mov_reg = regex.algorithm("moves")
            tps_reg = regex.positive_integer("tps")
            reg = re.compile(f"!animate\s*{scr_reg}?\s*{mov_reg}\s*{tps_reg}?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # make sure the algorithm isn't too long
            moves = Algorithm(groups["moves"])
            num_moves = len(moves)
            max_moves = 250
            if num_moves > max_moves:
                raise ValueError(f"number of moves ({num_moves}) must be at most {max_moves}")

            # if no scramble given, use the inverse of the moves
            if groups["scramble"] is None:
                scramble = PuzzleState()
                scramble.reset(4, 4)
                scramble.apply(moves.inverse())
            else:
                scramble = PuzzleState(groups["scramble"])

            # if no tps given, use 8 as a default
            if groups["tps"] is None:
                tps = 8
            else:
                tps = int(groups["tps"])
            time = round(num_moves/tps, 3)

            await message.channel.send("Working on it! It may take some time, please wait")

            msg  = f"{scramble}\n"
            msg += f"{moves} [{num_moves}]\n"
            msg += f"TPS (playback): {tps}\n"
            msg += f"Time (playback): {time}"

            make_video(scramble, moves, tps)
            await dh.send_binary_file("movie.webm", msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!analyse"):
        try:
            size_reg1 = regex.size("width1", "height1", "size1")
            size_reg2 = regex.size("width2", "height2", "size2")
            sol_reg = regex.algorithm("solution")
            reg = re.compile(f"!analyse((?P<single>(\s+{size_reg1})?(\s+{sol_reg}))|(?P<multi>(\s*{size_reg2})))")

            match = reg.fullmatch(command)
            groups = match.groupdict()

            if groups["single"] is not None:
                if groups["size1"] is not None:
                    width = int(groups["width1"])
                    height = int(groups["height1"])
                else:
                    width, height = 4, 4

                solution = Algorithm(groups["solution"])

                scramble = PuzzleState()
                scramble.reset(width, height)
                scramble.apply(solution.inverse())

                analysis = analyse(scramble, solution)

                optSolution = solver.solve(scramble, SolverRunType.ONE)

                msg  = f"Scramble: {scramble}\n"
                msg += f"Your solution [{len(solution)}]: {solution}\n"
                msg += f"Optimal solution [{len(optSolution)}]: {optSolution}\n"
                msg += "Analysis:"

                await dh.send_as_file(analysis, "analysis.txt", msg, message.channel)
            elif groups["multi"] is not None:
                if len(message.attachments) != 1:
                    raise Exception("no attached file found")

                text = await message.attachments[0].read()
                text = text.decode()

                # size
                width = int(groups["width2"])
                height = int(groups["height2"])

                # each solve is given as [scramble (optional)] [solution]
                scr_reg = regex.puzzle_state("scramble")
                sol_reg = regex.algorithm("solution")
                reg = re.compile(f"({scr_reg}\s*)?{sol_reg}")

                # solve each scramble and tally up the results
                results = {}
                opt_total = 0
                user_total = 0
                n = 0
                for match in reg.finditer(text):
                    n += 1

                    groups = match.groupdict()

                    solution = Algorithm(groups["solution"])
                    if groups["scramble"] is not None:
                        scramble = PuzzleState(groups["scramble"])
                    else:
                        scramble = PuzzleState()
                        scramble.reset(width, height)
                        scramble.apply(solution.inverse())

                    opt_len = len(solver.solve(scramble, SolverRunType.ONE))
                    user_len = len(solution)

                    opt_total += opt_len
                    user_total += user_len

                    diff = user_len - opt_len
                    if diff not in results:
                        results[diff] = 0
                    results[diff] += 1

                # write message
                opt_str = format(opt_total/n, ".3f")
                user_str = format(user_total/n, ".3f")
                diff_str = format((user_total-opt_total)/n, ".3f")

                msg = f"Optimal mean of {n}: {opt_str}\n"
                msg += f"Your mean: {user_str} (+{diff_str})\n"
                msg += "\n".join([f"+{k}: {v}" for (k, v) in sorted(results.items())])

                await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!draw"):
        try:
            state = PuzzleState(command[6:])
            img = draw_state(state)
            await dh.send_image(img, "scramble.png", "Your scramble:", message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getprob"):
        try:
            # !getprob [size: N or WxH] [mean/marathon length: optional] [moves: a-b or e.g. >=m, <m, =m, etc.] [repetitions: optional]
            size_reg = regex.size("width", "height")
            relay_reg = regex.relay("relay_start", "relay_end")
            full_size_reg = f"(?P<full_size>({size_reg}(?P<is_eut>\s*eut)?)|({relay_reg}))"
            solve_type_reg = "(?P<solve_type>(mo)|x)"
            num_solves_reg = regex.positive_integer("num_solves")
            full_solve_type_reg = "(" + solve_type_reg + num_solves_reg + ")"
            pos_real_reg = regex.positive_real()
            interval_reg = f"((?P<moves_from>{pos_real_reg})-(?P<moves_to>{pos_real_reg}))"
            comparison_reg = f"((?P<comparison>[<>]?=?)\s*(?P<moves>{pos_real_reg}))"
            reps_reg = regex.positive_integer("repetitions")
            reg = re.compile(f"!getprob(\s+{full_size_reg})(\s+{full_solve_type_reg})?(\s+(?P<range>{interval_reg}|{comparison_reg}))(\s+{reps_reg})?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # read solve type and number of solves
            if groups["solve_type"] is None:
                solve_type = "single"
                num_solves = 1
            elif groups["solve_type"] == "mo":
                solve_type = "mean"
                num_solves = int(groups["num_solves"])
            else:
                solve_type = "marathon"
                num_solves = int(groups["num_solves"])

            # limit on the number of solves
            if num_solves > 1000:
                raise ValueError("number of solves must be at most 1000")

            # read the size
            if groups["width"] is not None:
                # W or WxH size
                w = int(groups["width"])
                if groups["height"] is None:
                    h = w
                else:
                    h = int(groups["height"])

                # check if EUT or not
                if groups["is_eut"] is None:
                    # distribution for a single solve
                    dist = distributions.get_distribution(w, h)
                else:
                    dist = distributions.get_eut_distribution(w, h)
            else:
                # relay start-end
                start = int(groups["relay_start"])
                end = int(groups["relay_end"])

                # distribution for a single relay
                dist = distributions.get_relay_distribution(start, end)

            # distribution for the number of solves we want, instead of a single solve
            dist = dist.sum_distribution(num_solves)

            # check if range is given by interval or comparison, and calculate probability for one repetition
            multiplier = num_solves if solve_type == "mean" else 1
            if groups["comparison"] is None:
                start = round(multiplier * float(groups["moves_from"]))
                end = round(multiplier * float(groups["moves_to"]))
                prob_one = dist.prob_range(start, end)
            else:
                comp = comparison.from_string(groups["comparison"])
                moves = round(multiplier * float(groups["moves"]))
                prob_one = dist.prob(moves, comp)

            # number of repetitions
            if groups["repetitions"] is None:
                reps = 1
            else:
                reps = int(groups["repetitions"])

            # compute the probability of a scramble appearing at least once
            prob = 1 - (1 - prob_one)**reps

            # we rounded the range of moves, so we should display the rounded range instead of the original.
            # otherwise we would have messages like:
            # "Probability of 4x4 having an optimal solution of 52.1-52.9 moves is 14.80%"
            # even though we rounded 52.1 and 52.9 to 52 and 53.
            # if the endpoints of the rounded range are integers, make them integers, otherwise round to 3dp
            def make_str(a):
                if a % multiplier == 0:
                    return str(a // multiplier)
                return format(a/multiplier, ".3f")

            if groups["comparison"] is None:
                range_str = f"{make_str(start)}-{make_str(end)}"
            else:
                range_str = groups["comparison"] + make_str(moves)

            # write the message
            full_size = groups["full_size"]
            if solve_type == "single":
                msg = f"Probability of {full_size} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one out of {reps} within that range is {format_prob(prob)}"
            elif solve_type == "mean":
                msg = f"Probability of {full_size} mo{num_solves} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one mean out of {reps} within that range is {format_prob(prob)}"
            elif solve_type == "marathon":
                msg = f"Probability of {full_size} x{num_solves} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one marathon out of {reps} within that range is {format_prob(prob)}"

            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!paint"):
        good = False
        try:
            img_data = requests.get(message.attachments[0].url).content
            good = True
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"Please upload an image file!\n```\n{repr(e)}\n```")
        if good:
            contentArray = command.lower().split(" ")
            size = 50
            if len(contentArray) > 1:
                size = int(contentArray[1])
            with open("image_name.jpg", "wb") as handler:
                handler.write(img_data)
            my_img = cv2.imread("image_name.jpg")
            my_img = cv2.cvtColor(my_img, cv2.COLOR_BGR2GRAY)
            (thresh, my_img) = cv2.threshold(my_img, 100, 255, cv2.THRESH_BINARY)
            cv2.imwrite("image_name.jpg", my_img)
            with open("image_name.jpg", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Converted image: ", file=picture)
            my_img = cv2.imread("image_name.jpg")
            os.remove("image_name.jpg")
            h, w, a = my_img.shape
            desw = round(size / 2)
            bigger = max(w, h)
            if desw > 128:
                desw = 128
            ratio = 100 * (desw / bigger)
            scale_percent = ratio  # percent of original size
            w = math.ceil(w * scale_percent / 100)
            h = math.ceil(h * scale_percent / 100)
            dim = (w, h)
            bigger = max(w, h)
            puzzleSize = bigger * 2
            resized = cv2.resize(my_img, dim, interpolation=cv2.INTER_AREA)
            my_img = resized
            np.set_printoptions(threshold=sys.maxsize)
            convertedList = convertRgbToWeight(my_img)
            c = 0
            curline = 0
            curid = 0

            colors = np.zeros((h, w), dtype=int)
            for i in range(w * h):
                if convertedList[i] > 0.7:
                    colors[curline, curid] = 1
                curid = curid + 1
                if curid == w:
                    curid = 0
                    curline = curline + 1
            puzzle = np.zeros((puzzleSize, puzzleSize), dtype=int)
            c = 1
            for j in range(puzzleSize):
                for i in range(puzzleSize):
                    puzzle[j, i] = c
                    c = c + 1
            puzzle[puzzleSize - 1, puzzleSize - 1] = 0
            swaps = 0
            for i in range(h):
                for j in range(w):
                    if colors[i, j] == 1:
                        a, b = puzzle[i][j], puzzle[i + w][j]
                        puzzle[i][j], puzzle[i + w][j] = puzzle[i + w][j], puzzle[i][j]
                        if a != 0 and b != 0:
                            swaps = swaps + 1
                        a, b = puzzle[i][j + w], puzzle[i + w][j + w]
                        puzzle[i][j + w], puzzle[i + w][j + w] = (
                            puzzle[i + w][j + w],
                            puzzle[i][j + w],
                        )
                        if a != 0 and b != 0:
                            swaps = swaps + 1
            if (swaps % 2) != 0:
                a, b = (
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                )
                (
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                ) = (
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                )
            mystr = ""
            for x in puzzle:
                for y in x:
                    mystr = mystr + str(y) + " "
                mystr = mystr[:-1]
                mystr = mystr + "/"
            mystr = mystr[:-1]
            s = str(puzzleSize)
            msg = "Your scramble is ({s}x{s} sliding puzzle)\n(download file if its large):"
            await dh.send_as_file(mystr, "scramble.txt", msg, message.channel)
    elif command.startswith("!rev"):
        alg = Algorithm(command[5:])
        alg.invert()
        await message.channel.send(str(alg))
    elif command.startswith("!not"):
        alg = Algorithm(command[5:])
        alg.invert().revert()
        await message.channel.send(str(alg))
    elif command.startswith("!tti"):
        try:
            words = command[5:]
            r = requests.post(
                "https://api.deepai.org/api/text2img",
                data={
                    "text": words,
                },
                headers={"api-key": os.environ["aikey"]},
            )
            r = r.json()
            # print(r)
            img_data = requests.get(r["output_url"]).content
            with open("img_lemon.jpg", "wb") as handler:
                handler.write(img_data)
            with open("img_lemon.jpg", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Your weird image: ", file=picture)
            os.remove("img_lemon.jpg")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!datecompare"):
        pass
    elif command.startswith("!movesgame"):
        if message.channel.id == movesgame.channel.id:
            await movesgame.start()
    elif command.startswith("!tournament"):
        if message.channel.id == movesgame_tournament.channel.id:
            await movesgame_tournament.run()
    elif command.startswith("!game"):
        if message.channel.id == optimal_game.channel.id:
            await optimal_game.start()
    elif command.startswith("!goodm"):
        try:
            scramble = PuzzleState(command[7:])
            size = scramble.size()

            # don't allow daily fmc scramble
            for fmc in fmcs.values():
                if fmc.round.running():
                    fmc_scramble = fmc.round.get_scramble()
                    if scramble == fmc_scramble:
                        name = message.author.name
                        await message.channel.send(f"No cheating, {name}!")
                        return

            good_moves = [move.to_string(sol.first()) for sol in solver.solve(scramble, SolverRunType.GOOD)]
            good_moves_str = ", ".join(good_moves)

            msg  = f"Scramble: {scramble}\n"
            msg += f"Good moves: {good_moves_str}"

            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!eggsolve"):
        scramble = PuzzleState(command[10:])
        size = scramble.size()

        # don't allow daily fmc scramble
        for fmc in fmcs.values():
            if fmc.round.running():
                fmc_scramble = fmc.round.get_scramble()
                if scramble == fmc_scramble:
                    name = message.author.name
                    await message.channel.send(f"No cheating, {name}!")
                    return

        try:
            solutions = None
            result = solve_db.lookup(scramble)
            if result is not None:
                if result["all"]:
                    solutions = result["solutions"]
                    elapsed = None

            if solutions is None:
                a = perf_counter()
                solutions = solver.solve(scramble, SolverRunType.ALL)
                b = perf_counter()
                elapsed = b-a
                if elapsed >= 3:
                    solve_db.store(scramble, solutions, True)

            string = ""
            if elapsed is not None:
                string += f"Time: {round(elapsed, 3)}\n"
            string += f"Number of solutions: {len(solutions)}\n"
            string += f"Length: {len(solutions[0])}\n"
            string += "\n".join([str(s) for s in solutions])

            await dh.send_as_file(string, "solutions.txt", f"Scramble: {scramble}", message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!solve") or command.startswith("!video"):
        try:
            video = command.startswith("!video")

            scramble = PuzzleState(command[7:])
            size = scramble.size()

            # don't allow daily fmc scramble
            for fmc in fmcs.values():
                if fmc.round.running():
                    fmc_scramble = fmc.round.get_scramble()
                    if scramble == fmc_scramble:
                        name = message.author.name
                        await message.channel.send(f"No cheating, {name}!")
                        return

            # try looking up in list of known hard scrambles
            result = solve_db.lookup(scramble)
            if result is not None:
                solution = result["solutions"][0]
                elapsed = None
            else:
                a = perf_counter()
                solution = solver.solve(scramble, SolverRunType.ONE)
                b = perf_counter()
                elapsed = b-a
                if elapsed >= 3:
                    solve_db.store(scramble, [solution], False)

            # solution of solved puzzle = egg
            solution_str = str(solution)
            if solution_str == "":
                solution_str = ":egg:"

            msg  = f"Scramble: {scramble}\n"
            msg += f"Solution [{len(solution)}]: ||{solution_str}||\n"
            if elapsed is not None:
                msg += f"Time: {round(elapsed, 3)}"

            if video:
                msg += "\nPlease wait! I'm making a video for you!"

            await message.channel.send(msg)

            if video:
                make_video(scramble, solution, 8)
                await dh.send_binary_file("movie.webm", "", message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!simplify"):
        try:
            alg = Algorithm(command[10:])
            old_len = len(alg)
            alg.simplify()
            new_len = len(alg)
            await message.channel.send(f"[{old_len} -> {new_len}] {alg}")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!solvable"):
        try:
            pos = PuzzleState(command[10:])
            if pos.solvable():
                msg = "solvable"
            else:
                msg = "unsolvable"
            await message.reply(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!8fmc"):
        try:
            if len(command) == 5:
                n = 100
            else:
                n = int(command[6:])
                n = max(1, min(1000, n))

            data = ""
            l = []
            for i in range(n):
                scramble = scrambler.getScramble(3)
                solution = solver.solve(scramble, SolverRunType.ONE)
                length = len(solution)

                # generate real scramble
                prefix = Algorithm("D2 R2 U2 L2 D2 R2 U2 L2")
                puzzle = PuzzleState()
                puzzle.reset(3)
                puzzle.apply(prefix.inverse())
                puzzle.apply(solution.inverse())
                real_scramble = prefix + solver.solve(puzzle, SolverRunType.ONE).inverse()
                real_scramble.simplify()

                l.append(length)
                data += f"{scramble}\t{real_scramble}\t{length}\n"

            msg  = f"Average: {round(sum(l)/n, 3)}\n"
            msg += f"Longest: {max(l)}\n"
            msg += f"Shortest: {min(l)}"

            await dh.send_as_file(data, "8fmc.txt", msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!rank"):
        try:
            user = command[6:]
            if user == "":
                user = link.get_leaderboard_user(message.author.id)

            msg = lb_commands.rank(user)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!link"):
        if not permissions.is_egg_admin(message.author):
            return
        try:
            reg = re.compile(f"!link\s+(?P<user_id>[0-9]+)\s+(?P<lb_username>[a-zA-Z0-9]+)")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            user_id = int(groups["user_id"])
            lb_username = groups["lb_username"]

            link.link(user_id, lb_username)
            await message.channel.send("Accounts linked")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!addsolve"):
        try:
            if not permissions.is_egg_admin(message.author):
                raise Exception("you don't have permission")

            if len(message.attachments) != 1:
                raise Exception("no attached file found")

            state_reg = regex.puzzle_state("state")
            reg = re.compile(f"!addsolve(\s+{state_reg})(\s+(?P<is_all>all))?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            text = await message.attachments[0].read()
            text = text.decode()

            state = PuzzleState(groups["state"])
            solutions = [Algorithm(x) for x in text.splitlines()]

            if groups["is_all"] is None:
                is_all = False
            else:
                is_all = True

            stored = solve_db.store(state, solutions, is_all)
            if stored:
                await message.channel.send(f"Stored {len(solutions)} solutions")
            else:
                await message.channel.send("Not updated")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!deletesolve"):
        try:
            if not permissions.is_egg_admin(message.author):
                raise Exception("you don't have permission")

            state_reg = regex.puzzle_state("state")
            reg = re.compile(f"!deletesolve\s+{state_reg}")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError("failed to parse arguments")

            groups = match.groupdict()
            state = PuzzleState(groups["state"])
            if solve_db.delete(state):
                await message.channel.send("Deleted solutions")
            else:
                await message.channel.send("Nothing to delete")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command == "!egg":
        with open("misc/egg.txt", "r") as f:
            egg = f.read()
        await message.channel.send("```" + egg + "```")
    elif command == "!rareegg":
        scores = random_games["egg"].scores()
        msg = ""
        for id, score in scores.items():
            user = bot.get_user(id)
            if user:
                msg += f"{user.name}: {score}\n"
        await message.channel.send(msg)
    elif command == "!rareyaytso":
        scores = random_games["yaytso"].scores()
        msg = ""
        for id, score in scores.items():
            user = bot.get_user(id)
            if user:
                msg += f"{user.name}: {score}\n"
        await message.channel.send(msg)
    elif command.startswith("!help"):
        await message.channel.send("Egg bot commands: https://github.com/benwh1/eggbot/blob/master/README.md")
    elif command.startswith("!restart"):
        if permissions.is_egg_admin(message.author):
            await message.channel.send("Restarting...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Restarted"
            bot_helper.restart()
    elif command.startswith("!dbdump"):
        if permissions.is_owner(message.author):
            my_db = {}
            for key in db.keys():
                my_db[key] = db[key]
            await dh.send_as_file(serialize.serialize(my_db), "db.txt", "", message.channel)
    elif command.startswith("!getdif"):
        content_array = command.lower().split(" ")
        NMlist = content_array[1].split("x")
        n = float(NMlist[0])
        m = float(NMlist[1])
        t = float(content_array[2])
        dif = (t / (n*m*(n+m))) * (1 + math.log(max(n/m, m/n)/2 + 0.5)) * math.log(n*m) * (1 + 2 ** (4.5-n*m/6)) / 4.7 * 2000
        await message.channel.send(str(dif))
    elif command.startswith("!md"):
        try:
            scr_reg = regex.puzzle_state("scramble")
            reg = re.compile(f"!md\s*{scr_reg}")

            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()
            scramble = PuzzleState(groups["scramble"])
            w, h = scramble.size()

            md = manhattan.md(scramble)
            msg = f"md={md}"

            if w == h:
                m = manhattan.md_mean(w)
                s = manhattan.md_variance(w)**0.5
                dist = statistics.NormalDist(mu=m, sigma=s)
                prob = dist.cdf(md)
                std_diff = (md-m)/s

                msg += f"\n{w}x{h} mean={m}\n"
                msg += f"{w}x{h} std={s:.3f}\n"
                if std_diff < 0:
                    msg += f"{md} is {-std_diff:.3f} standard deviations below the mean\n"
                else:
                    msg += f"{md} is {std_diff:.3f} standard deviations above the mean\n"
                msg += f"Estimated probability of {w}x{h} md<={md} is {format_prob(prob)}"

            await message.reply(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")

# keep_alive()
bot.run(os.environ["token"])
