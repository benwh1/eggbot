def format(tps):
    if tps is None:
        return "None"
    if tps == 2147483647:
        return "∞"
    if tps % 1000 == 0:
        return str(tps // 1000)
    else:
        return str(tps / 1000)
