# eggbot
Egg bot for sliding puzzle discord server
https://discord.gg/7vXrWAS3yZ

WR commands:
- !getwr [NxM] - get WR single for NxM puzzle
- !wrsby [username] - get all WRs by that username

FMC commands
- !fmc - get current fmc information
- !submit [solution] - submit solution to current fmc
- !results - get results of current fmc
- !startfmc - start new 10 minute fmc

Movesgame commands
- !movesgame - start new movesgame
- !tournament - start new movesgame tournament
- !results - view lifetime results of movesgame

PB/ranks commands
- !getpb [user=you] [puzzle=NxM] - get user's PBs. default puzzle size is 4x4, or the channel size in the 3x3-10x10 channels
- !getreq [tier] [puzzle=NxN] - get time requirement for a tier. default puzzle size is the same as for !getpb
- !getlb - get current version of the webpage as a text file
- !update - update the ranks webpage and WR pages
- !datecompare [date1] [date2] - compare two states of leaderboard (!datecompare 2021-06-14 2021-06-13)

Solver-related commands:
- !solve [scramble] - optimally solve a scramble (3x3 or 4x4)
- !eggsolve [scramble] - find all optimal solutions (3x3 or 4x4)
- !goodm [scramble] - find good moves for a scramble (3x3 or 4x4)
- !video [scramble] - same as !solve but also generates a video
- !analyse [solution] - analyse a solution and find mistakes
- !analyse3x3 - upload a file containing solutions (one per line). calculates how many were optimal, +2, +4, etc.

Scramble/solution-related commands:
- !rev [solution] - reverse the solution of scramble, use RLUD notation, you can also use numbers like in slidysim
- !not [solution] - change notation (R = L, U = D) etc. of the solution
- !draw [scramble] - draws image of a 4x4 scramble
- !animate [scramble=solution-inverse] [solution] [tps=8] - makes an animation of your solve (4x4 only)
- !getreal - generates a scramble algorithm and draws a picture of it
- !getscramble [N=4] - generates a random scramble for an NxN puzzle
- !simplify [solution] - removes mistakes like UD or LR from a solution
- !solvable [scramble] - check if a position is solvable

Misc. commands:
- !getprob [NxM] mo[N=1] [moves-range] [repetitions=1] - compute probability of an NxM single/mean having an optimal solution length within a given range of moves, after some number of attempts
- !paint [size] - paint image into slidysim scramble, use size to  make it custom puzzles size (up to 256), you should upload image as attachment 
- !8fmc [N=100] - generate N random scrambles and optimal solution lengths, for use with 8 puzzle 100x fmc
- !egg - 🥚
- !help - link to this file
- !tti [text] - bad AI image generator

List of useful websites:
- Ranks - https://yaytso.herokuapp.com/
- WRs - https://slidysim.com/records.html
- WRs (all) - https://slidysim.com/records_all.html
- WRs (moves) - https://slidysim.com/records_moves.html
- WRs (moves, all) - https://slidysim.com/records_all_moves.html
