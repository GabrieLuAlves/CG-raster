import numpy as np
from os import path, mkdir
from PIL import Image

import matplotlib.pyplot as plt

from typing import List, Tuple


Resolution = Tuple[int, int]
Point = Tuple[float, float]
Line = Tuple[Point, Point]
Polygon = Tuple[List[Point], List[Tuple[int, int]]]

class Field:
    def __init__(self, resolution: Resolution):
        self._resolution = resolution

        self._lines: List[Line] = []
        self._polygons: List[Polygon] = []
    
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, val: Resolution):
        self._resolution = val
    
    def add_line(self, line: Line) -> None:
        self._lines.append(line)
    
    def add_polygon(self, polygon: Polygon):
        self._polygons.append(polygon)
    
    def _map_points(self, points: List[Point]) -> List[Point]:
        width, height = self._resolution

        kw = width / 2
        kh = height / 2

        points = [(0.999, y) if x == 1 else (x, y) for x, y in points]
        points = [(x, 0.999) if y == 1 else (x, y) for x, y in points]
        points = [(x + 1.0, y + 1.0) for x, y in points]
        points = [(x * kw, y * kh) for x, y in points]

        return points

    def _draw_polygon(self, polygon: Polygon):
        vertices, connections = polygon

        vertices = self._map_points(vertices)

        for i in range(len(vertices)):
            x, y = vertices[i]
            vertices[i] = np.floor(x) + 0.5, np.floor(y) + 0.5

        
        x_left, _ = vertices[0]
        x_right, _ = vertices[0]

        for i in range(1, len(vertices)):
            x, _ = vertices[i]
            if x_left > x:
                x_left = x
            elif x_right < x:
                x_right = x
    
        points = []
        
        path = list(filter(lambda c: vertices[c[0]][0] != vertices[c[1]][0], connections))

        length = int(x_right - x_left + 1)
        for x in np.linspace(x_left, x_right, num=length):
            intercepted_y: List[float] = []
            
            for i, j in path:
                x1, y1 = vertices[i]
                x2, y2 = vertices[j]

                m = ((y1 - y2) / (x1 - x2))
                n = y1 - m * x1

                xa, xb = (x1, x2) if x1 <= x2 else (x2, x1)

                if x1 < x2 and xa <= x and x < xb:
                    intercepted_y.append(m * x + n)

                elif x1 > x2 and xa < x and x <= xb:
                    intercepted_y.append(m * x + n)

            if len(intercepted_y) == 2:
                points.append(self._raster_line((x, intercepted_y[1]), (x, intercepted_y[0])))
            elif len(intercepted_y) == 1:
                points.append(np.array([[x, intercepted_y[0]]]).astype('int32'))
            else:
                raise Exception(f'Unexpeced error. Number of intercepted lines in polygon rasterization was {len(intercepted_y)}')        
        points = np.concatenate(points, axis=0)

        return points
        
    def _raster_line(self, start_point: Point, end_point: Point) -> np.ndarray:
        points: List[List[int]] = []

        if start_point == end_point:
            return np.floor(np.array([start_point])).astype(dtype='int32')

        x1, y1 = np.floor(start_point) + 0.5
        x2, y2 = np.floor(end_point) + 0.5

        if np.abs(x1 - x2) >= np.abs(y1 - y2):
            m = (y1 - y2) / (x1 - x2)
            n = y1 - m * x1

            x = x1 if x1 <= x2 else x2
            xf = x2 if x1 <= x2 else x1
            
            while x <= xf:
                points.append([x, m * x + n])
                x = x + 1

        else:
            m = (x1 - x2) / (y1 - y2)
            n = x1 - m * y1

            y = y1 if y1 <= y2 else y2
            yf = y2 if y1 <= y2 else y1
            
            while y <= yf:
                points.append([m * y + n, y])
                y = y + 1

        M = np.array(points)
        M = np.floor(M).astype(dtype=np.int32)

        return M

    def render(self) -> np.ndarray:
        columns, rows = self._resolution
        field = np.zeros((rows, columns))

        for polygon in self._polygons:
            points = self._draw_polygon(polygon)
            for x, y in points:
                field[y][x] = 1

        for start_point, end_point in self._lines:
            [start_point, end_point] = self._map_points([
                start_point, end_point
            ])

            line_points = self._raster_line(start_point, end_point)
            for x, y in line_points:
                field[y][x] = 1

        return np.flip(field, 0)

def new_polygon(vertices: List[Point]) -> Polygon:
    connections: List[Tuple[int, int]] = [(x, x + 1) for x in range(len(vertices) - 1)]
    connections.append((len(vertices) - 1, 0))

    return (vertices, connections)

def new_rectangle(center: Point, width: float, height: float) -> Polygon:
    x, y = center

    width, height = width / 2, height / 2

    return new_polygon([
        (x - width, y + height),
        (x + width, y + height),
        (x + width, y - height),
        (x - width, y - height),
    ])

def new_diamond(center: Point, width: float, height: float) -> Polygon:
    x, y = center

    width, height = width / 2, height / 2

    return new_polygon([
        (x - width, y),
        (x, y + height),
        (x + width, y),
        (x, y - height),
    ])

def main():
    resolutions: List[Resolution] = [
        (  20,   20),
        ( 100,  100),
        ( 300,  300),
        ( 500,  500),
        ( 720,  400),
        ( 720,  480),
        ( 800,  600),
        ( 800,  800),
        (1000, 1000),
        (1024,  768),
        (1024, 1024),
        (1280,  720),
        (1366,  768),
    ]
    '''
    for resolution in resolutions:
        field = Field(resolution)

        field.add_line(((+1.00, +0.00), (-1.00, -0.00)))
        field.add_line(((+0.95, +0.31), (-0.95, -0.31)))
        field.add_line(((+0.81, +0.59), (-0.81, -0.59)))
        field.add_line(((+0.59, +0.81), (-0.59, -0.81)))
        field.add_line(((+0.31, +0.95), (-0.31, -0.95)))
        field.add_line(((+0.00, +1.00), (-0.00, -1.00)))
        field.add_line(((-0.95, +0.31), (+0.95, -0.31)))
        field.add_line(((-0.81, +0.59), (+0.81, -0.59)))
        field.add_line(((-0.59, +0.81), (+0.59, -0.81)))
        field.add_line(((-0.31, +0.95), (+0.31, -0.95)))

        if not path.exists(path.join('.', 'images')):
            mkdir(path.join('.', 'images'))

        file_name = path.join('.', 'images', f'lines-{resolution[0]}x{resolution[1]}.png')
        matrix = field.render()

        plt.imsave(file_name, matrix)
    '''
    for resolution in resolutions:
        field = Field(resolution)

        ## UPPER 3
        field.add_polygon(new_diamond(
            center=(-0.666, +0.666),
            width=0.4,
            height=0.4,
        ))

        field.add_polygon(new_diamond(
            center=(+0.000, +0.666),
            width=0.4,
            height=0.4,
        ))
        
        field.add_polygon(new_diamond(
            center=(+0.666, +0.666),
            width=0.4,
            height=0.4,
        ))

        ## LOWER 3
        field.add_polygon(new_diamond(
            center=(-0.666, -0.666),
            width=0.4,
            height=0.4,
        ))

        field.add_polygon(new_diamond(
            center=(+0.000, -0.666),
            width=0.4,
            height=0.4,
        ))

        field.add_polygon(new_diamond(
            center=(+0.666, -0.666),
            width=0.4,
            height=0.4,
        ))

        ## CENTER 2
        field.add_polygon(new_diamond(
            center=(-0.333, +0.000),
            width=0.4,
            height=0.4,
        ))
        
        field.add_polygon(new_diamond(
            center=(+0.333, +0.000),
            width=0.4,
            height=0.4,
        ))
    
        file_name = path.join('.', 'images', f'quadrilateral-{resolution[0]}x{resolution[1]}.png')
        matrix = field.render()

        plt.imsave(file_name, matrix)
    


if __name__ == '__main__':
    main()