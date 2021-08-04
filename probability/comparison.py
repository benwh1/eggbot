from enum import Flag

class Comparison(Flag):
    Null               = 0
    LessThan           = 1
    Equal              = 2
    GreaterThan        = 4
    LessThanOrEqual    = LessThan | Equal
    GreaterThanOrEqual = GreaterThan | Equal
    NotEqual           = LessThan | GreaterThan
    All                = LessThan | Equal | GreaterThan

def from_string(str):
    dict = {
        "<"  : Comparison.LessThan,
        ""   : Comparison.Equal,
        "="  : Comparison.Equal,
        ">"  : Comparison.GreaterThan,
        "<=" : Comparison.LessThanOrEqual,
        ">=" : Comparison.GreaterThanOrEqual,
        "!=" : Comparison.NotEqual,
    }

    if str not in dict:
        raise ValueError(f"cannot convert string \"{str}\" to Comparison")

    return dict[str]
