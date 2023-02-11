import base64
import datetime as dt
import os
import requests
from log import log
import json
import zlib
import leaderboard.leaderboard as lb
import leaderboard.tiers as tiers
import leaderboard.categories as categories
import leaderboard.ranking as ranking
from database import db

# filters the leaderboard results, removing any results that don't correspond
# to one of our categories. each result has a "category" parameter appended
# which is the index of the category in leaderboard.categories.categories.
def get_category_results():
    # get the full leaderboard
    full_lb = lb.get_leaderboard()

    # filter the results
    filtered_lb = []
    entries = ["width", "height", "solvetype", "avglen"]
    for result in full_lb:
        result_category = {x : result[x] for x in entries}
        try:
            # add the category index for convenience
            index = categories.categories.index(result_category)
            result["category"] = index
            filtered_lb.append(result)
        except ValueError as e:
            continue

    # sort by username
    filtered_lb.sort(key=lambda x: x["user"])

    return filtered_lb

# creates a dict of the form {username : [list of category times]}
# where the i'th element of the list of times is the users time in
# the i'th category in leaderboard.categories.categories.
def results_table():
    results = get_category_results()
    users = sorted(set(x["user"] for x in results))

    table = {}

    for user in users:
        # create an empty row with one entry per category
        row = [None]*len(categories.categories)

        for result in results:
            if result["user"] != user:
                continue

            category = result["category"]

            # fill in the entry in the table with the users best time.
            # note that there may be multiple results in the leaderboard
            # if the user has done solves with both control schemes,
            # so we need to choose the fastest one.
            if row[category] is None:
                row[category] = result["time"]
            else:
                row[category] = min(row[category], result["time"])

        # add the users results to the table
        table[user] = row

    return table

def update():
    log.info("Running update")

    # store results
    table = results_table()
    today = dt.datetime.now().strftime("%Y-%m-%d")
    db[f"leaderboard/data/{today}"] = table

    # store usernames sorted by power
    sorted_table = ranking.sort_table(table)
    usernames = list(sorted_table.keys())

    # store sorted list of usernames in db
    db["leaderboard/usernames"] = usernames

    # update the webpage
    # get sorted list of all dates that we have data for
    dates = [x[17:] for x in db.prefix("leaderboard/data/")]
    dates.sort()

    # create a dict of the form {date : data, ...} to be written to data.js
    data_dict = {}
    for date in dates:
        # read the data from the database and uncompress it
        table = db[f"leaderboard/data/{date}"]

        # sort the data and make it into a table of the form
        # [[user, place, power, results], ...]
        # that we can compress and write into a js array
        sorted_table = ranking.sort_table(table)
        formatted_table = []
        for i, user in enumerate(sorted_table):
            # add row but replace None with -1 in the results
            new_row = [user, i+1, ranking.power(sorted_table[user])]
            new_row += [x if x is not None else -1 for x in sorted_table[user]]
            formatted_table.append(new_row)
        table_str = json.dumps(formatted_table)

        # compress the table string and convert to base 64
        compressed_str = zlib.compress(table_str.encode(), level=9)
        base64_str = base64.b64encode(compressed_str).decode()

        data_dict[date] = base64_str

    # write data.js file
    file  = "export const tiers = " + json.dumps(tiers.tiers) + ";\n"
    file += "export const categories = " + json.dumps(categories.category_names) + ";\n"
    file += "export const data = " + json.dumps(data_dict) + ";\n"
    with open("web/data.js", "w") as f:
        f.write(file)

    # update wr list
    requests.get(os.environ["updateURL"], timeout=5).text

    log.info("Finished update")
