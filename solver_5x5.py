import os
import re
import subprocess

from algorithm import Algorithm
from puzzle_state import PuzzleState

def get_input(puzzle: PuzzleState):
    # if puzzle is not 5x5, throw an error
    if puzzle.size() != (5, 5):
        raise ValueError("puzzle is not 5x5")
    flat_arr = [x for row in puzzle.arr for x in row]
    numbers = [-int(val) % 25 for val in flat_arr]
    reversed_numbers = numbers[::-1]
    result = ','.join(map(str, reversed_numbers))
    return result

def read_solution(puzzle: PuzzleState, output: str):
    numbers = list(map(int, output.split(',')))

    # find gap position and prepend it to the output
    flat_arr = [x for row in puzzle.arr for x in row]
    gap = 24 - flat_arr.index(0)
    numbers.insert(0, gap)

    differences = [numbers[i+1]-numbers[i] for i in range(len(numbers)-1)]
    mapping = {-5: 'U', -1: 'L', 5: 'D', 1: 'R'}
    result = ''.join(mapping.get(diff, '') for diff in differences)

    return Algorithm(result).simplify()

def solve(puzzle: PuzzleState):
    if puzzle.size() != (5, 5):
        raise ValueError("puzzle is not 5x5")

    binary = os.environ["solver_5x5_binary"]
    pdbdir = os.environ["solver_5x5_pdbdir"]
    catalogue = os.environ["solver_5x5_catalogue"]

    command = f"{binary} -d {pdbdir} -j 4 {catalogue}"
    input = get_input(puzzle)

    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.stdin.write(input)
    process.stdin.close()

    output = ""
    for line in process.stdout:
        if line.startswith("Solution found: "):
            output = line
            break
    
    process.kill()

    return read_solution(puzzle, output[16:])
