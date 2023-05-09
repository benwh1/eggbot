from leaderboard import tiers
from formatting import time as time_format

def category_pb(category, data, pbtype="time"):
    best = None
    for result in data:
        if result["solvetype"] == category["solvetype"] and result["avglen"] == category["avglen"]:
            if best is None:
                best = result[pbtype]
            else:
                if pbtype == "tps":
                    best = max(best, result[pbtype])
                else:
                    best = min(best, result[pbtype])
    return best

def get_tier_name(tier):
    if tier is None:
        tier_name = "Unranked"
    else:
        tier_name = tier["name"]
    return tier_name

def get_next_tier(tier):
    if tier is None:
        next_tier = tiers.tiers[0]
    else:
        tier_index = tiers.tiers.index(tier)
        if tier_index == len(tiers.tiers)-1:
            next_tier = None
        else:
            next_tier = tiers.tiers[tier_index+1]
    return next_tier

def get_requirement_message(tier, category_index):
    if tier is None:
        requirement_msg = None
    else:
        next_tier_name = tier["name"]
        next_tier_req = tier["times"][category_index]
        requirement_msg = f"{next_tier_name}={time_format.format(next_tier_req)}"
    return requirement_msg

def get_used_sizes(categories):
    return {(category["width"],category["height"]) for category in categories}
