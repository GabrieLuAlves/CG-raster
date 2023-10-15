import numpy as np
from os import path
from PIL import Image

import matplotlib.pyplot as plt

from typing import List, Tuple

def draw_line(resolution: Tuple[int, int], P: np.ndarray):
    width, height = resolution
    
    kw = (width - 0.000001) / 2
    kh = (height - 0.000001) / 2

    M = np.array([[kw, 0], [0, kh]]) \
        .dot(np.concatenate((P, np.ones((2, 1))), axis=1)) \
        .dot(np.array([[1, 0], [0, 1], [1, 1]]))
 
    dx = M[0][0] - M[0][1]
    dy = M[1][0] - M[1][1]

    if np.abs(dx) >= np.abs(dy):
        [x0, x1] = np.floor(M[0]) + 0.5

        m = dy / dx
        n = M[1][0] - m * M[0][0]


        length = int(np.floor(x1) - np.floor(x0) + 1)

        M = np.array([
            np.linspace(x0, x1, num=length),
            np.ones(length)
        ])

        M = np.array([[1, 0], [m, n]]).dot(M)

    else:
        [y0, y1] = M[1]

        m = dx / dy
        n = M[0][0] - M[1][0] * m

        length = int(np.floor(y1) - np.floor(y0) + 1)

        M = np.array([
            np.linspace(y0, y1, num=length),
            np.ones(length)
        ])

        M = np.array([[m, n], [1.0, 0.0]]).dot(M)
    

    print(M)
    M = np.floor(M).astype(dtype=np.int32)

    return M

def print_in_field(lines: List[np.ndarray], resolution: Tuple[int, int]):
    columns, rows = resolution
    field = np.zeros((rows, columns))

    for line in lines:
        line[1] = rows - 1 - line[1]
        for x, y in np.transpose(line):
            field[y][x] = 1
    
    return field

def main():
    for resolution in [
        (  20,   20),
        (  40,   40),
        (  60,   60),
        (  80,   80),
        ( 720,  400),
        ( 720,  480),
        ( 800,  600),
        (1024,  768),
        (1280,  720),
        (1366,  768),
        ( 300,  300),
        ( 500,  500),
        ( 800,  800),
    ]:
        line_1 = draw_line(
            resolution,
            np.array([
                [-1.0, +1.0],
                [+0.0, +1.0]
        ])
    )

        line_2 = draw_line(
            resolution,
            np.array([
                [-1.0, +1.0],
                [+0.0, -1.0]
            ])
        )
        line_3 = draw_line(
            resolution,
            np.array([
                [+1.0, +1.0],
                [-1.0, +1.0]
            ])
        )

        line_4 = draw_line(
            resolution,
            np.array([
                [-1.0, +1.0],
                [+0.0, +0.0]
            ])
        )

        line_5 = draw_line(
            resolution,
            np.array([
                [+0.0, +0.0],
                [-1.0, +1.0]
            ])
        )

        lines = [
            line_1,
            line_2,
            line_3,
        ]

        field = print_in_field(lines, resolution)

        plt.imsave(path.join('.', 'images', f'{resolution[0]}x{resolution[1]}.png'), field)


if __name__ == '__main__':
    main()