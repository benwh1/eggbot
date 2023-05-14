import copy
import move
from prettytable import PrettyTable
import solver
from solver import SolverRunType
from puzzle_state import PuzzleState

def analyse(scramble, solution):
    # copy the scramble
    scramble = copy.deepcopy(scramble)

    table = PrettyTable()
    table.field_names = ["N", "State", "Setup", "Move", "Better", "Your ending", "Better ending", "Your+opt"]

    # the optimal solution of the scramble
    opt_end = solver.solve(scramble, SolverRunType.ONE)

    for i in range(1, len(solution)):
        # the first i moves of our solution
        user_start = solution.take(i)

        # apply the next move
        next_move = solution.at(i-1)
        scramble.move(next_move)

        # optimal solution of position with i-1 moves applied
        last_opt_end = opt_end

        # solutions of the position with i moves applied
        opt_end = solver.solve(scramble, SolverRunType.ONE)
        user_end = solution.drop(i)

        # the optimal solution length increased, so this is a mistake
        if len(opt_end) == len(last_opt_end) + 1:
            N = i

            scramble.undo_move(next_move)
            state = str(scramble)
            scramble.move(next_move)
            
            setup = str(user_start.rdrop(1))
            bad_move = move.to_string(next_move)
            better = move.to_string(last_opt_end.first())
            your_ending = str(solution.drop(i-1))
            better_ending = str(last_opt_end)
            your_plus_opt = setup + better_ending

            table.add_row([N, state, setup, bad_move, better, your_ending, better_ending, your_plus_opt])

        # user end is optimal, so we don't need to calculate any further
        if len(opt_end) == len(user_end):
            break

    return table.get_string()
