import leaderboard.leaderboard as lb
from leaderboard.categories import categories, category_names
from leaderboard import tiers
from leaderboard import ranking
from leaderboard import db
from leaderboard import update as lb_update
from leaderboard import commands_helper as helper
import leaderboard.username as names
from formatting import time as time_format
from formatting import moves as moves_format
import json

def get_pb(width, height, user, pbtype="time"):
    username = names.find_username(user)

    # formatter + dumb thing
    if pbtype == "time":
        formatter = time_format.format
        pbtype2 = "time"
    elif pbtype == "move" or pbtype == "moves":
        formatter = moves_format.format
        pbtype = "move"
        pbtype2 = "moves"
    elif pbtype == "tps":
        formatter = moves_format.format
        pbtype2 = "tps"
    else:
        raise ValueError("unsupported or invalid `pbtype`")

    # get all the relevant data in one leaderboard call
    data = lb.get_leaderboard(width, height, user=username, pbtype=pbtype)

    # {category: message text} pairs
    results = {}

    for result in data:
        result_msg = ""
        category = {
            "width": width,
            "height": height,
            "solvetype": result["solvetype"],
            "avglen": result["avglen"]
        }

        # ranked category result
        if category in categories and pbtype == "time":
            idx = categories.index(category)

            # find the users pb for this category
            best = helper.category_pb(category, data, pbtype=pbtype2)

            # find the tier of this result
            tier = tiers.result_tier(idx, best)
            tier_name = helper.get_tier_name(tier)

            # find the next tier above the users tier so we can show the requirement
            next_tier = helper.get_next_tier(tier)

            requirement_msg = helper.get_requirement_message(next_tier, idx)

            result_msg += f"{category_names[idx]}: {formatter(best)} ({tier_name})"
            if requirement_msg is not None:
                result_msg += f" ({requirement_msg})"
        # not a main category, but a standard average
        elif result["solvetype"] == "Standard":
            avglen = result["avglen"]

            best = helper.category_pb(category, data, pbtype=pbtype2)

            if avglen == 1:
                name = "single"
            else:
                name = f"ao{avglen}"

            result_msg += f"{width}x{height} {name}: {formatter(best)}"
        else:
            continue

        # convert category to string because dict isn't hashable
        cat_str = json.dumps(category)
        results[cat_str] = result_msg

    results_list = [(json.loads(x), y) for (x, y) in results.items()]
    standard = sorted([x for x in results_list if x[0]["solvetype"] == "Standard"], key=lambda x: x[0]["avglen"])
    nonstandard = [x for x in results_list if x[0]["solvetype"] != "Standard"]
    results = standard + nonstandard

    msg = f"{width}x{height} PBs for {username}\n"
    msg += "```\n"
    msg += "\n".join([x[1] for x in results])
    msg += "\n```"

    return msg

def get_req(width, height, tier_name):
    tier = tiers.get_tier(tier_name)
    real_tier_name = tier["name"]

    msg = f"Requirements for {real_tier_name} {width}x{height}\n"
    msg += "```\n"
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            req = tier["times"][i]
            msg += f"{category_names[i]}: {time_format.format(req)}\n"
    msg += "```"

    return msg

def rank(user):
    username = names.find_username(user)
    table = db.latest_results()
    position = ranking.place(table, username)
    power = ranking.power(table[username])
    power_tier = tiers.power_tier(power)
    name = power_tier["name"]
    msg = f"{username} is in position {position} with {power} power ({name})"

    next_tier = helper.get_next_tier(power_tier)
    if next_tier is not None:
        next_name = next_tier["name"]
        required = next_tier["limit"]
        return f"{msg} ({next_name}={required})"

    return msg

def update():
    lb_update.update()
