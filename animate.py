import copy
import cv2
import numpy as np
from draw_state import draw_state

def make_video(scramble, solution, tps, bypass_limit=False):
    # opencv video writer
    w, h = scramble.size()
    size = (100*w, 100*h)
    writer = cv2.VideoWriter("movie.webm", cv2.VideoWriter_fourcc(*'VP90'), tps, size)

    # create a copy so we don't modify the original
    pos = copy.deepcopy(scramble)

    def write_frame():
        # draw the state and send it to the video writer
        image = draw_state(pos, bypass_limit=bypass_limit)
        cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        writer.write(cv2_image)

    # draw the first frame before any moves were applied
    write_frame()

    # draw the rest of the frames
    for i in range(len(solution)):
        pos.move(solution.at(i))
        write_frame()

    # finish the video
    writer.release()
