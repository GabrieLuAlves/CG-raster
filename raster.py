import numpy as np
from os import path, mkdir
from PIL import Image

import matplotlib.pyplot as plt

from typing import List, Tuple


Resolution = Tuple[int, int]
Point = Tuple[float, float]

class Field:
    def __init__(self, resolution: Resolution):
        self._resolution = resolution

        self._lines: List[Tuple[Point, Point]] = []
    
    def add_line(self, start_point: Point, end_point: Point) -> None:
        self._lines.append((start_point, end_point))
    
    def _draw_line(self, start_point: Point, end_point: Point) -> np.ndarray:
        width, height = self._resolution

        M = np.array([
            start_point,
            end_point,
        ])

        M[M == 1] = 0.999999

        M = np.transpose(M)

        kw = (width) / 2
        kh = (height) / 2

        M = np.concatenate(
            (M, np.ones((1, 2))),
            axis=0
        )

        M = np.array([[kw, 0, kw], [0, kh, kh]]).dot(M)
    
        dx = M[0][0] - M[0][1]
        dy = M[1][0] - M[1][1]

        if np.abs(dx) >= np.abs(dy):
            [x0, x1] = np.floor(M[0])

            m = dy / dx
            n = M[1][0] - m * M[0][0]

            length = int(np.abs(x1 - x0) + 1)

            M = np.array([
                np.linspace(x0, x1, num=length),
                np.ones(length)
            ])

            M = np.array([[1, 0], [m, n]]).dot(M)

        else:
            [y0, y1] = np.floor(M[1])

            m = dx / dy
            n = M[0][0] - M[1][0] * m

            length = int(np.abs(y1 - y0) + 1)

            M = np.array([
                np.linspace(y0, y1, num=length),
                np.ones(length)
            ])

            M = np.array([[m, n], [1.0, 0.0]]).dot(M)

        M = np.floor(M).astype(dtype=np.int32)

        return M

    def render(self) -> np.ndarray:
        columns, rows = self._resolution
        field = np.zeros((rows, columns))

        for start_point, end_point in self._lines:
            for x, y in np.transpose(self._draw_line(start_point, end_point)):
                field[y][x] = 1

        return np.flip(field, 0)
    
def main():
    resolutions: List[Resolution] = [
        (  20,   20),
        (  21,   21),
        (  40,   40),
        (  60,   60),
        (  80,   80),
        ( 300,  300),
        ( 500,  500),
        ( 720,  400),
        ( 720,  480),
        ( 800,  600),
        ( 800,  800),
        (1024,  768),
        (1280,  720),
        (1366,  768),
    ]

    for resolution in resolutions:
        field = Field(resolution)

        field.add_line((+0.0, +1.0), (+0.5, +0.0))
        field.add_line((+0.5, +0.0), (+0.0, -1.0))
        field.add_line((+0.0, -1.0), (-0.5, +0.0))
        field.add_line((-0.5, +0.0), (+0.0, +1.0))

        if not path.exists(path.join('.', 'images')):
            mkdir(path.join('.', 'images'))

        file_name = path.join('.', 'images', f'{resolution[0]}x{resolution[1]}.png')
        matrix = field.render()

        plt.imsave(file_name, matrix)


if __name__ == '__main__':
    main()