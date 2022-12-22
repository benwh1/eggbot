def format_long(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d == 0:
        if h == 0:
            if m == 0:
                return f"{s} seconds"
            return f"{m} minutes, {s} seconds"
        return f"{h} hours, {m} minutes, {s} seconds"
    return f"{d} days, {h} hours, {m} minutes, {s} seconds"

def format(time):
    if time is None:
        return "None"

    s, z = divmod(time, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    if time < 1000:
        return f"0.{z:03d}"
    elif time < 60000:
        return f"{s}.{z:03d}"
    elif time < 3600000:
        return f"{m}:{s:02d}.{z:03d}"
    else:
        return f"{h}:{m:02d}:{s:02d}.{z:03d}"
