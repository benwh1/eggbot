def n_min(a,b):
    """
    Special min for comparison of two values which could include `None`.
    `None` is only chosen if there is no other value. 
    """
    if a is None:
        return b
    if b is None:
        return a
    return min(a,b)

def n_max(a,b):
    """
    Special max for comparison of two values which could include `None`.
    `None` is only chosen if there is no other value. 
    """
    if a is None:
        return b
    if b is None:
        return a
    return max(a,b)

