import os
import requests

def get_leaderboard(width=-1, height=-1, solvetype="any", avglen=-1, pbtype="time", user=""):
    url = os.environ["slidysim"]
    r = requests.post(url, data = {
        "width"       : width,
        "height"      : height,
        "solvetype"   : solvetype,
        "displaytype" : "Standard",
        "avglen"      : avglen,
        "pbtype"      : pbtype,
        "sortby"      : "time",
        "controls"    : "km",
        "user"        : user,
        "solvedata"   : 0,
        "version"     : "29.0"
    }, timeout=15
    )

    if r.text[-7:] != "success":
        raise Exception("failed to read leaderboard")

    data = [line.split(",") for line in r.text[19:].split("<br>")[:-1]]

    leaderboard = []
    for row in data:
        leaderboard.append({
            "width"       : int(row[0]),
            "height"      : int(row[1]),
            "solvetype"   : row[2],
            "displaytype" : row[3],
            "user"        : row[4],
            "time"        : int(row[5]),
            "moves"       : int(row[6]),
            "tps"         : int(row[7]),
            "avglen"      : int(row[8]),
            "controls"    : row[9],
            "pbtype"      : row[10],
            "timestamp"   : int(row[12])
        })

    return leaderboard
