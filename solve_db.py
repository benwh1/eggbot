from database import db
from algorithm import Algorithm

db_key = "solver/4x4/solutions"

if db_key not in db:
    db[db_key] = {}

def lookup(state):
    data = db[db_key]

    scramble_str = str(state)
    if scramble_str in data:
        # look up the result and convert from strings to Algorithms
        result = data[scramble_str]
        result["solutions"] = [Algorithm(s) for s in result["solutions"]]
        return result
    else:
        return None

# is_all is True if we are storing all solutions, false if we only have one
def store(state, solutions, is_all):
    data = db[db_key]

    # True if either the scramble is not already stored, or if we previously
    # only had one solution but now we have all.
    should_update = False

    scramble_str = str(state)

    if scramble_str not in data:
        should_update = True
    elif is_all:
        result = data[scramble_str]
        if not result["all"]:
            should_update = True

    if should_update:
        data[scramble_str] = {
            "solutions": [str(s) for s in solutions],
            "all": is_all
        }
        db[db_key] = data

    return should_update

def delete(state):
    data = db[db_key]
    scramble_str = str(state)

    if scramble_str in data:
        del data[scramble_str]
        db[db_key] = data
        return True
    return False
