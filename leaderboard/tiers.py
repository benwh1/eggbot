from leaderboard.categories import categories

with open("leaderboard/data/tier_names.txt", "r") as f:
    tier_names = f.read().strip().split("\n")
    f.close()

with open("leaderboard/data/tier_power.txt", "r") as f:
    tier_power = [int(x) for x in f.read().strip().split("\n")]
    f.close()

with open("leaderboard/data/tier_limits.txt", "r") as f:
    tier_limits = [int(x) for x in f.read().strip().split("\n")]
    f.close()

with open("leaderboard/data/tier_times.txt", "r") as f:
    tier_times = [[int(x) for x in row.split(",")] for row in f.read().strip().split("\n")]
    f.close()

assert len(tier_names) == len(tier_power) == len(tier_limits) == len(tier_times)

tiers = []
for i in range(len(tier_names)):
    assert len(categories) == len(tier_times[i])

    tiers.append({
        "name"  : tier_names[i],
        "power" : tier_power[i],
        "limit" : tier_limits[i],
        "times" : tier_times[i]
    })

def get_tier(name):
    for tier in tiers:
        if name.lower() in tier["name"].lower():
            return tier
    raise ValueError("invalid tier name")

def result_tier(category_index, time):
    if time is None:
        return None

    for tier in reversed(tiers):
        if time <= tier["times"][category_index]:
            return tier

    return None

def power_tier(power):
    for tier in reversed(tiers):
        if power >= tier["limit"]:
            return tier

    return None

def true_tier(results_list):
    min_tier = None
    for i, result in enumerate(results_list):
        tier = result_tier(i, result)
        if tier is None:
            return get_tier("Unranked")
        if min_tier is None:
            min_tier = tier
        elif min_tier["power"] > tier["power"]:
            min_tier = tier
    return min_tier
