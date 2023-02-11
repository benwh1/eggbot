from puzzle_state import PuzzleState

def md_mean(n: int) -> int:
    return (2*n**3 - 5*n + 3) // 3

def md_variance(n: int) -> float:
    return (8*n**4 + 13*n**2 - 15) / 90

def md(puzzle: PuzzleState) -> int:
    total = 0
    w, h = puzzle.size()
    for y in range(h):
        for x in range(w):
            a = puzzle.arr[y][x]
            if a == 0:
                continue
            sx, sy = (a-1)%w, (a-1)//w
            total += abs(x-sx) + abs(y-sy)
    return total
