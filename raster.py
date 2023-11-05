import numpy as np
import numpy.typing as npt

from time import time_ns

from os import path, mkdir

import PIL.Image
from PIL.Image import Image

from typing import List, Tuple


Resolution = Tuple[int, int]
Point = Tuple[float, float]
Line = Tuple[Point, Point]
Polygon = Tuple[List[Point], List[Tuple[int, int]]]
HermiteCurve = Tuple[Point, Point, Tuple[float, float], Tuple[float, float]]


class PointModifier:
    def __init__(self, points: List[Point]):
        self._points = points
        
        self._scale_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

        self._rotation_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

        self._move_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points: List[Point]):
        self._points = points

    def scale(self, x_factor: float, y_factor: float):
        self._rotation_matrix = np.array([
            [x_factor, 0, 0],
            [0, y_factor, 0],
            [0, 0, 1]
        ])

        return self

    def rotate(self, angle_rads: float):
        self._rotation_matrix = np.array([
            [np.cos(angle_rads), -np.sin(angle_rads), 0],
            [np.sin(angle_rads), np.cos(angle_rads), 0],
            [0, 0, 1]
        ])

        return self

    def move(self, x_dist, y_dist):
        self._move_matrix = np.array([
            [1, 0, x_dist],
            [0, 1, y_dist],
            [0, 0, 1]
        ])

        return self

    def _get_points(self) -> List[Point]:
        return [
            (x, y) for x, y in np.transpose(
                self._move_matrix \
                .dot(self._scale_matrix) \
                .dot(self._rotation_matrix) \
                .dot(np.transpose(
                    np.append(
                        np.array(self._points),
                        np.ones((len(self._points), 1)),
                        axis=1
                    )
                ))
            )[:, :2]
        ]

    def get_points(self) -> List[Point]:
        return self._get_points()

    def __call__(self) -> List[Point]:
        return self._get_points()

class Field:
    def __init__(self, resolution: Resolution):
        self._resolution = resolution

        self._lines: List[Line] = []
        self._polygons: List[Polygon] = []
        self._curves: List[Tuple[HermiteCurve, int]] = []


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


    def add_hermite_curve(self, curve: HermiteCurve, n_points: int):
        self._curves.append((curve, n_points))

    def _raster_polygon(self, polygon: Polygon) -> npt.NDArray[np.int32]:
        vertices, edges = polygon
        columns, rows = self._resolution
    
        draft_field = np.full((rows, columns), 0, dtype=np.uint8)

        edges_cells_list: List[npt.NDArray[np.int32]] = []

        for i, j in edges:
            point_a = vertices[i]
            point_b = vertices[j]
            edges_cells_list.append(
                self._raster_line(
                    (point_a[0], point_a[1]),
                    (point_b[0], point_b[1]),
                )
            )

        edges_cells = np.vstack(edges_cells_list)
        del edges_cells_list

        for i in range(len(edges_cells)):
            x = edges_cells[i, 0]
            y = edges_cells[i, 1]

            if x < 0:
                x = 0
            elif x >= columns:
                x = columns - 1

            if y < 0:
                y = 0
            elif y >= rows:
                y = rows - 1
            
            edges_cells[i, 0] = x
            edges_cells[i, 1] = y

        for x, y in edges_cells:        
            draft_field[y, x] = 1
        
        max_y = np.max(edges_cells[:, 1])
        min_y = np.min(edges_cells[:, 1])
        min_x = np.min(edges_cells[:, 0])
        max_x = np.max(edges_cells[:, 0])

        t1 = time_ns()
        inner_polygon_cells: List[npt.NDArray] = []

        for y in range(max_y, min_y - 1, -1):
            current = 0
            changes = 0
            for x in range(min_x, max_x + 1):
                if draft_field[y, x] != current:
                    current = draft_field[y, x]
                    changes += 1
                
            if changes == 2:
                continue
            
            current = 0
            changes = 0
            for x in range(min_x, max_x + 1):
                if draft_field[y, x] != current:
                    changes += 1
                    current = draft_field[y, x]
                
                if (changes / 2) % 2 == 1:
                    inner_polygon_cells.append(np.array([x, y]))
        
        t2 = time_ns()

        string = f'Time to raster {max_x - min_x + 1}x{max_y - min_y + 1}' + f'polygon: {(t2 - t1) / 10 ** 3}'
        print(string)

        return np.vstack([
            edges_cells,
            np.vstack(inner_polygon_cells),
        ])

        

    def _raster_hermite_curve(self, curve: HermiteCurve, n_points: int) -> np.ndarray:
        p1, p2, t1, t2 = curve

        points_t: List[float] = [t / (n_points - 1) for t in range(n_points)]

        input_matrix = np.array(
            [np.array([np.power(t, 3), np.power(t, 2), np.power(t, 1), 1]) for t in points_t]
        )

        coeficients_matrix = np.array([
            [+2, -2, +1, +1],
            [-3, +3, -2, -1],
            [+0, +0, +1, +0],
            [+1, +0, +0, +0],
        ])

        parameters_matrix = np.array([
            p1,
            p2,
            t1,
            t2,
        ])

        M = input_matrix.dot(coeficients_matrix).dot(parameters_matrix)

        x1, y1 = M[0, :]

        points: List[npt.NDArray[np.int32]] = []
        for x2, y2 in M[1:, :]:
            points.append(self._raster_line((x1, y1), (x2, y2)))
            x1, y1 = x2, y2
        
        return np.vstack(points)


    def _raster_line(self, start_point: Point, end_point: Point) -> npt.NDArray[np.int32]:
        if start_point == end_point:
            return np.floor(np.array([start_point])).astype(dtype='int32')

        columns, rows = self._resolution

        x1, y1 = start_point
        x2, y2 = end_point

        if x1 == 1.0:
            x1 = 0.999999
            
        if x2 == 1.0:
            x2 = 0.999999
            
        if y1 == 1.0:
            y1 = 0.999999
            
        if y2 == 1.0:
            y2 = 0.999999

        x1 += 1
        x2 += 1
        y1 += 1
        y2 += 1

        x1 *= columns / 2.0
        x2 *= columns / 2.0
        y1 *= rows / 2.0
        y2 *= rows / 2.0

        if np.abs(x1 - x2) >= np.abs(y1 - y2):
            m = (y1 - y2) / (x1 - x2)
            n = y1 - m * x1

            x = x1 if x1 <= x2 else x2
            xf = x2 if x1 <= x2 else x1

            d = np.round(x - np.floor(x), 2)
            num = int(np.floor(xf) - np.floor(x) + 1)
            x_values = np.linspace(np.floor(x), np.floor(xf), num=num, dtype=np.float32)
            x_values += d

            M = np.array([
                x_values,
                x_values * m + n
            ])

        else:
            m = (x1 - x2) / (y1 - y2)
            n = x1 - m * y1

            y = y1 if y1 <= y2 else y2
            yf = y2 if y1 <= y2 else y1
            
            d = np.round(y - np.floor(y), 2)
            num = int(np.floor(yf) - np.floor(y) + 1)
            y_values = np.linspace(np.floor(y), np.floor(yf), num=num, dtype=np.float32)
            y_values += d
            
            M = np.array([
                y_values * m + n,
                y_values,
            ])

        return np.transpose(np.floor(M).astype(dtype=np.int32))

    def render(self) -> Image:
        columns, rows = self._resolution
        points: List[np.ndarray] = []

        for polygon in self._polygons:
            points.append(self._raster_polygon(polygon))

        for curve, n_points in self._curves:
            points.append(self._raster_hermite_curve(curve, n_points))

        for start_point, end_point in self._lines:
            points.append(self._raster_line(start_point, end_point))      


        img = PIL.Image.new('RGB', (columns, rows), "black")
        pixels = img.load()

        M = np.concatenate(points, axis=0)
        for x, y in M:
            try:
                pixels[x, y] = (255, 255, 255)
            except IndexError:
                ...
        
        return img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)


def new_polygon(vertices: List[Point]) -> Polygon:
    edges: List[Tuple[int, int]] = [(x, x + 1) for x in range(len(vertices) - 1)]
    edges.append((len(vertices) - 1, 0))

    return (vertices, edges)


def new_triangle(center: Point, sides_sizes: Tuple[float, ...]) -> Polygon:
    x_center, y_center = center

    if len(sides_sizes) == 1:
        half_base = sides_sizes[0] / 2.0
        half_height = sides_sizes[0] * 0.4330

        return new_polygon([
            (x_center, y_center + half_height),
            (x_center + half_base, y_center - half_height),
            (x_center - half_base, y_center - half_height)]
        )
    
    elif len(sides_sizes) == 2:
        half_base = min(sides_sizes) / 2.0
        half_height = np.sqrt(np.square(max(sides_sizes)) - np.square(half_base))

        return new_polygon([
            (x_center, y_center + half_height),
            (x_center + half_base, y_center - half_height),
            (x_center - half_base, y_center + half_height)]
        )
    
    elif len(sides_sizes) == 3:
        raise NotImplementedError()

    else:
        raise Exception('The sizes array length must be at least 1 and at maximum 3')


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


def new_hexagon(center: Point, side: float) -> Polygon:
    half_height = side * 0.866
    half_side = side / 2

    x, y = center

    return new_polygon([
        (x - half_side, y + half_height),
        (x + half_side, y + half_height),
        (x + side, y),
        (x + half_side, y - half_height),
        (x - half_side, y - half_height),
        (x - side, y),
    ])


def main():

    # resolutions: List[Resolution] = [
    #     ( 100, 1000),
    #     ( 100,  100),
    #     ( 300,  300),
    #     ( 500,  500),
    #     ( 720,  400),
    #     ( 720,  480),
    #     ( 800,  600),
    #     ( 800,  800),
    #     (1000, 1000),
    #     (1001, 1001),
    #     (1024,  768),
    #     (1024, 1024),
    #     (1280,  720),
    #     (1366,  768),
    # ]

    # for resolution in resolutions:
    #     field = Field(resolution)

    #     point_modifier = PointModifier([
    #         (-1.0, +0.0),
    #         (+1.0, +0.0)
    #     ])

    #     angles = [
    #         -np.pi / 12,    -np.pi / 6,         -np.pi / 4,
    #         -np.pi / 3,     -np.pi / 12 * 5,    0,
    #         +np.pi / 12,    +np.pi / 6,         +np.pi / 4,
    #         +np.pi / 3,     +np.pi / 12 * 5,    +np.pi / 2
    #     ]

    #     radii = [1.0, 0.75, 0.5, 0.25]
        
    #     for angle in angles:
    #         [p1, p2] = point_modifier.rotate(angle).get_points()
    #         field.add_line((p1, p2))
        
    #     for radius in radii:
    #         field.add_hermite_curve((
    #             (+0.0, +radius),
    #             (+radius, +0.0),
    #             (+1.675 * radius, +0.0),
    #             (+0.0, -1.675 * radius),
    #         ), 20)
    #         field.add_hermite_curve((
    #             (+radius, +0.0),
    #             (+0.0, -radius),
    #             (+0.0, -1.675 * radius),
    #             (-1.675 * radius, +0.0),
    #         ), 20)
    #         field.add_hermite_curve((
    #             (+0.0, -radius),
    #             (-radius, +0.0),
    #             (-1.675 * radius, +0.0),
    #             (+0.0, +1.675 * radius),
    #         ), 20)
    #         field.add_hermite_curve((
    #             (-radius, +0.0),
    #             (+0.0, +radius),
    #             (+0.0, +1.675 * radius),
    #             (+1.675 * radius, +0.0),
    #         ), 20)
        
    #     random_numbers = np.random.random((16, 2))
    #     random_numbers[:, 0] = 0.75 * random_numbers[:, 0] + 0.1
    #     random_numbers[:, 1] = 2 * np.pi * random_numbers[:, 1]

    #     aux_column = np.copy(random_numbers[:, 0])

    #     random_numbers[:, 0] = aux_column * np.cos(random_numbers[:, 1])
    #     random_numbers[:, 1] = aux_column * np.sin(random_numbers[:, 1])

    #     if not path.exists(path.join('.', 'generated_images')):
    #         mkdir(path.join('.', 'generated_images'))

    #     file_name = path.join('.', 'generated_images', f'lines-{resolution[0]}x{resolution[1]}.png')
    #     field.render().save(file_name)


    # for resolution in resolutions:
    #     field = Field(resolution)

    #     ## UPPER 3
    #     field.add_polygon(new_diamond(
    #         center=(-0.666, +0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     field.add_polygon(new_diamond(
    #         center=(+0.000, +0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))
        
    #     field.add_polygon(new_diamond(
    #         center=(+0.666, +0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     ## LOWER 3
    #     field.add_polygon(new_diamond(
    #         center=(-0.666, -0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     field.add_polygon(new_diamond(
    #         center=(+0.000, -0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     field.add_polygon(new_diamond(
    #         center=(+0.666, -0.666),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     ## CENTER 2
    #     field.add_polygon(new_diamond(
    #         center=(-0.333, +0.000),
    #         width=0.4,
    #         height=0.4,
    #     ))
        
    #     field.add_polygon(new_diamond(
    #         center=(+0.333, +0.000),
    #         width=0.4,
    #         height=0.4,
    #     ))

    #     field.add_line(((-1, -0.333), (1, -0.333)))
    #     field.add_line(((-1, +0.333), (1, +0.333)))

    #     field.add_line(((-0.333, -1), (-0.333, +1)))
    #     field.add_line(((+0.333, -1), (+0.333, +1)))
    
    #     file_name = path.join('.', 'generated_images', f'quadrilateral-{resolution[0]}x{resolution[1]}.png')
    #     field.render().save(file_name)
    
    field = Field((100, 100))
    field.add_polygon(new_triangle((-1, 0), (1.6,)))
    field.render().save('overflowed_triangle.png')

if __name__ == '__main__':
    main()