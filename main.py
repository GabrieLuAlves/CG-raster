from math import cos, sin, sqrt, pi

from PIL import ImageTk, Image
from tkinter import Button, Canvas, END, Entry, FALSE, Frame, Label, OptionMenu, StringVar, Tk

import numpy as np
import os

from raster import Field, new_triangle, new_hexagon, new_rectangle

ROOT_WIDTH = 1900
ROOT_HEIGHT = 1000
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
RESOLUTIONS = [
    (100, 100),
    (300, 300),
    (800, 600),
    (1920, 1080)
]


class Interface:
    def __init__(self):
        self.root = Tk()

        self.root.title("Geração de imagens")
        self.root.geometry(f"{ROOT_WIDTH}x{ROOT_HEIGHT}")
        self.root.resizable(width=FALSE, height=FALSE)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        outputFrame = Frame(self.root, width=1500, height=850)
        outputFrame.grid_propagate(FALSE)
        outputFrame.grid(row=0, column=0)
        outputFrame.grid_rowconfigure(1, weight=1)
        outputFrame.grid_columnconfigure(1, weight=1, minsize=ROOT_WIDTH / 2)

        upperOutputFrame = Frame(outputFrame)
        lowerOutputFrame = Frame(outputFrame)
        upperOutputFrame.grid(row=0, column=1)
        lowerOutputFrame.grid(row=2, column=1)

        separator = Frame(outputFrame, width=25, height=25)
        separator.grid(row=1, column=0)

        self.imageFramesDict = dict()
        self.textLabelsDict = dict()

        for index in range(0, 4):
            master = upperOutputFrame if index < 2 else lowerOutputFrame
            column = index % 2

            self.imageFramesDict[index] = Frame(master)
            self.imageFramesDict[index].grid(row=1, column=column)

            self.textLabelsDict[index] = Label(master,
                                               text=f"{RESOLUTIONS[index][0]}x{RESOLUTIONS[index][1]}",
                                               font=('Times New Roman', 15))
            self.textLabelsDict[index].grid(row=0, column=column)

        self.imageLabelsDict = dict()
        self.tkImages = []

        for index, frame in self.imageFramesDict.items():

            resolution = RESOLUTIONS[index]

            aspect_ratio = resolution[0] / resolution[1]

            current_image = f"images/default.png"
            img = Image.open(current_image).resize(size=(CANVAS_WIDTH, round(CANVAS_HEIGHT / aspect_ratio)))
            self.tkImages.append(ImageTk.PhotoImage(img))
            self.imageLabelsDict[index] = Label(frame, image=self.tkImages[index])
            self.imageLabelsDict[index].pack()

        inputFrame = Frame(self.root, width=ROOT_WIDTH / 2, height=ROOT_HEIGHT)
        inputFrame.grid_propagate(FALSE)
        inputFrame.grid(row=0, column=1)
        inputFrame.columnconfigure(0, weight=1)
        inputFrame.columnconfigure(1, weight=1)

        inputValuesFrame = Frame(inputFrame)
        inputValuesFrame.grid(row=0, column=0, sticky='n')
        previewFrame = Frame(inputFrame)
        previewFrame.grid(row=0, column=1)

        self.generate_line_input(inputValuesFrame, 0)

        self.generate_polygon_input(inputValuesFrame, 2)

        self.generate_hermite_input(inputValuesFrame, 6)

        self.canvas = MyCanvas(previewFrame, CANVAS_WIDTH, CANVAS_HEIGHT, 0, 1)

        buttonsFrames = Frame(previewFrame)
        buttonsFrames.grid(row=2, column=1)

        self.reset_button = Button(buttonsFrames, text='Reset', command=self.reset_canvas)
        self.reset_button.grid(row=0, column=0, pady=(10, 0), padx=(0, 10))

        self.results_button = Button(buttonsFrames, text='Gerar Resultados', command=self.generate_results)
        self.results_button.grid(row=0, column=1, pady=(10, 0), padx=(0, 10))

    def generate_line_input(self, masterFrame, base_row):
        Label(masterFrame, width=15, height=1, background='pink', text='Adicionar linha').grid(row=base_row,
                                                                                               column=0,
                                                                                               padx=20,
                                                                                               pady=(30, 20))
        lineInputFrame = Frame(masterFrame)
        lineInputFrame.grid(row=base_row + 1, column=0, sticky='w')
        Label(lineInputFrame, text='Insira os pontos:').grid(row=1, column=0, padx=(0, 10))

        Label(lineInputFrame, text='x1').grid(row=1, column=1)
        lineInputEntryx1 = Entry(lineInputFrame, width=10)

        Label(lineInputFrame, text='y1').grid(row=1, column=3)
        lineInputEntryy1 = Entry(lineInputFrame, width=10)

        Label(lineInputFrame, text='x2').grid(row=2, column=1)
        lineInputEntryx2 = Entry(lineInputFrame, width=10)

        Label(lineInputFrame, text='y2').grid(row=2, column=3)
        lineInputEntryy2 = Entry(lineInputFrame, width=10)

        self.lineInputEntryList = (lineInputEntryx1, lineInputEntryy1, lineInputEntryx2, lineInputEntryy2)

        lineInputEntryx1.grid(row=1, column=2, padx=5)
        lineInputEntryy1.grid(row=1, column=4, padx=5)
        lineInputEntryx2.grid(row=2, column=2, padx=5)
        lineInputEntryy2.grid(row=2, column=4, padx=5)

        Frame(lineInputFrame).grid(row=1, column=5, padx=5)

        LineInputButton = Button(lineInputFrame, command=self._add_line, width=5, height=1, text='Enviar',
                                 padx=10)
        LineInputButton.grid(row=1, column=6)

    def generate_polygon_input(self, masterFrame, base_row):
        Label(masterFrame, width=15, height=1, background='pink', text='Adicionar Poligono').grid(row=base_row,
                                                                                                  column=0,
                                                                                                  padx=20,
                                                                                                  pady=20)
        self.polygonInputFrame = Frame(masterFrame)
        self.polygonInputFrame.grid(row=base_row + 1, column=0, sticky='w')

        Label(self.polygonInputFrame, text='Escolha o polígono:').grid(row=1, column=0)

        options = ('Triângulo', 'Quadrado', 'Hexágono')
        self._selectedOption = StringVar()
        self._selectedOption.set(options[0])

        self.polygonsDropdown = OptionMenu(self.polygonInputFrame, self._selectedOption, *options)
        self.polygonsDropdown.grid(row=1, column=1)

        Label(self.polygonInputFrame, text='Ponto central (x, y):').grid(row=2, column=0, padx=15)
        Label(self.polygonInputFrame, text='Tamanho do lado:').grid(row=3, column=0)
        polygonInputEntryx1 = Entry(self.polygonInputFrame, width=10)

        polygonInputEntryy1 = Entry(self.polygonInputFrame, width=10)

        polygonInputEntryx2 = Entry(self.polygonInputFrame, width=10)

        polygonInputEntryx1.grid(row=2, column=1, padx=5, pady=5)
        polygonInputEntryy1.grid(row=2, column=3, padx=5, pady=5)
        polygonInputEntryx2.grid(row=3, column=1, padx=5, pady=5)

        self.polygonInputEntryList = [
            polygonInputEntryx1,
            polygonInputEntryy1,
            polygonInputEntryx2]

        polygonInputButton = Button(self.polygonInputFrame, command=self._add_polygon, width=5, height=1, text='Enviar',
                                    padx=10)
        polygonInputButton.grid(row=2, column=6, sticky='n', padx=(10, 0))

    def generate_hermite_input(self, masterFrame, base_row):
        Label(masterFrame, width=24, height=1, background='pink', text='Adicionar curva de Hermite').grid(
            row=base_row,
            column=0,
            padx=20,
            pady=20,
            sticky='n',
        )

        hermiteInputFrame = Frame(masterFrame)
        hermiteInputFrame.grid(row=base_row + 1, column=0)

        Label(hermiteInputFrame, text='Insira os pontos:').grid(row=1, column=0, padx=(0, 10))

        Label(hermiteInputFrame, text='x1', height=1).grid(row=1, column=1)
        hermiteInputEntryx1 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='y1', height=1).grid(row=1, column=3)
        hermiteInputEntryy1 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='x2', height=1).grid(row=2, column=1)
        hermiteInputEntryx2 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='y2', height=1).grid(row=2, column=3)
        hermiteInputEntryy2 = Entry(hermiteInputFrame, width=10)

        hermiteInputEntryx1.grid(row=1, column=2, padx=5)
        hermiteInputEntryy1.grid(row=1, column=4, padx=5)
        hermiteInputEntryx2.grid(row=2, column=2, padx=5)
        hermiteInputEntryy2.grid(row=2, column=4, padx=5)

        Label(hermiteInputFrame, text='Insira os vetores T1 e T2:').grid(row=3, column=0, padx=(0, 10))

        Label(hermiteInputFrame, text='Tx1').grid(row=3, column=1)
        hermiteInputEntryTx1 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='Ty1').grid(row=3, column=3)
        hermiteInputEntryTy1 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='Tx2').grid(row=4, column=1)
        hermiteInputEntryTx2 = Entry(hermiteInputFrame, width=10)

        Label(hermiteInputFrame, text='Ty2').grid(row=4, column=3)
        hermiteInputEntryTy2 = Entry(hermiteInputFrame, width=10)

        hermiteInputEntryTx1.grid(row=3, column=2, padx=5)
        hermiteInputEntryTy1.grid(row=3, column=4, padx=5)
        hermiteInputEntryTx2.grid(row=4, column=2, padx=5)
        hermiteInputEntryTy2.grid(row=4, column=4, padx=5)

        Label(hermiteInputFrame, text='Insira a quantidade de pontos:').grid(row=5, column=0, padx=(0, 10))

        Label(hermiteInputFrame, text='P').grid(row=5, column=1)

        hermiteInputEntryP = Entry(hermiteInputFrame, width=10)
        hermiteInputEntryP.grid(row=5, column=2)

        self.hermiteInputEntryList = (
            hermiteInputEntryx1, hermiteInputEntryy1,
            hermiteInputEntryx2, hermiteInputEntryy2,
            hermiteInputEntryTx1, hermiteInputEntryTy1,
            hermiteInputEntryTx2, hermiteInputEntryTy2,
            hermiteInputEntryP,
        )

        Frame(hermiteInputFrame, bg='blue').grid(row=1, column=5, padx=5)

        LineInputButton = Button(hermiteInputFrame, command=self._add_hermite_curve, width=5, text='Enviar',
                                 padx=10)
        LineInputButton.grid(row=1, column=6)

    def _add_line(self):

        list_of_dots = []

        try:
            if not all(
                [
                    -1 <= float(element.get().strip()) <= 1 for element in self.lineInputEntryList
                    ]):
                    raise ValueError

            for entry in self.lineInputEntryList:
                value = float(entry.get().strip())
                list_of_dots.append(value)
                entry.delete(0, END)

            p1 = tuple(list_of_dots[:2])
            p2 = tuple(list_of_dots[2:])

            self.canvas.create_line(
                self.canvas.width / 2 + (list_of_dots[0] * (self.canvas.width / 2)),
                self.canvas.height / 2 + (list_of_dots[1] * -(self.canvas.width / 2)),
                self.canvas.width / 2 + (list_of_dots[2] * (self.canvas.width / 2)),
                self.canvas.height / 2 + (list_of_dots[3] * -(self.canvas.width / 2)),
                fill='red',
                width=1,
                tags='generated')
            self.canvas.line_draws.append((p1, p2))

        except ValueError:
            pass

    def _add_polygon(self, dropdown=None, option=None, mode=None):

        list_of_dots = []
        try:

            x = float(self.polygonInputEntryList[0].get().strip())
            y = float(self.polygonInputEntryList[1].get().strip())
            p = float(self.polygonInputEntryList[2].get().strip())

            if not all(
                    [-1 <= x <= 1,
                     -1 <= y <= 1,
                     0 < p <= 2]):
                raise ValueError

            for entry in self.polygonInputEntryList:
                list_of_dots.append(float(entry.get().strip()))
                entry.delete(0, END)

            vertices = list()
            color = str()

            if self._selectedOption.get() == 'Triângulo':

                center_x = self.canvas.width / 2 + (list_of_dots[0] * (self.canvas.width / 2))
                center_y = self.canvas.height / 2 + (list_of_dots[1] * -(self.canvas.width / 2))

                x1 = center_x - ((list_of_dots[2] * self.canvas.width / 2)) / 2
                y1 = center_y + (((sqrt(3) / 2) * list_of_dots[2] * self.canvas.width) / 2) / 2
                x2 = center_x
                y2 = center_y + (((sqrt(3) / 2) * list_of_dots[2] * -self.canvas.width) / 2) / 2
                x3 = center_x + ((list_of_dots[2] * self.canvas.width) / 2) / 2
                y3 = y1

                vertices = [x1, y1, x2, y2, x3, y3]

                color = 'green'

            elif self._selectedOption.get() == 'Quadrado':

                center_x = self.canvas.width / 2 + (list_of_dots[0] * (self.canvas.width / 2))
                center_y = self.canvas.height / 2 + (list_of_dots[1] * -(self.canvas.width / 2))

                x1 = center_x - (list_of_dots[2] * self.canvas.width / 2) / 2
                y1 = center_y - (list_of_dots[2] * -(self.canvas.width / 2)) / 2
                x2 = center_x + (list_of_dots[2] * self.canvas.width / 2) / 2
                y2 = center_y + (list_of_dots[2] * -(self.canvas.width / 2)) / 2

                vertices = [x1, y1, x2, y2]

                color = 'yellow'
                self.canvas.create_rectangle(vertices, fill=color, width=1, tags='generated')
                self.canvas.polygon_draws['Quadrado'].append((
                    tuple(list_of_dots[:2]),
                    list_of_dots[2]))
                return

            elif self._selectedOption.get() == 'Hexágono':
                for i in range(6):
                    angle = 2 * pi / 6 * i
                    x = (list_of_dots[0] + list_of_dots[2] * cos(angle)) * (self.canvas.width / 2)
                    y = (list_of_dots[1] + list_of_dots[2] * sin(angle)) * (-self.canvas.height / 2)
                    x += (self.canvas.width / 2)
                    y += (self.canvas.height / 2)
                    vertices.extend((x, y))

                color = 'blue'

            else:
                return

            self.canvas.create_polygon(vertices, fill=color, width=1, tags='generated')
            self.canvas.polygon_draws[self._selectedOption.get()].append((
                tuple(list_of_dots[:2]),
                list_of_dots[2]))

        except ValueError:
            pass

    def _add_hermite_curve(self):
        try:
            list_of_dots = [float(entry.get().strip()) for entry in self.hermiteInputEntryList]
            if not all(
                    [
                        -1 <= list_of_dots[0] <= 1,
                        -1 <= list_of_dots[1] <= 1,
                        -1 <= list_of_dots[2] <= 1,
                        -1 <= list_of_dots[3] <= 1,
                        0 < list_of_dots[8],
                    ]
            ):
                raise ValueError

            for entry in self.hermiteInputEntryList:
                entry.delete(0, END)

            print(list_of_dots)

            p0 = tuple(list_of_dots[:2])
            p1 = tuple(list_of_dots[2:4])
            t0 = tuple(list_of_dots[4:6])
            t1 = tuple(list_of_dots[6:8])
            p = int(list_of_dots[-1])

            """
            for point in range(0, len(list_of_dots) - 1, 2):
                list_of_dots[point] = self.canvas.width / 2 + list_of_dots[point] * (self.canvas.width / 2)

            for point in range(1, len(list_of_dots) - 1, 2):
                list_of_dots[point] = self.canvas.height / 2 + list_of_dots[point] * -(self.canvas.height / 2)
            print(list_of_dots)


            """

            normalized_vector = list_of_dots.copy()
            for point in range(0, 4, 2):
                normalized_vector[point] = self.canvas.width / 2 + normalized_vector[point] * (self.canvas.width / 2)

            for point in range(1, 5, 2):
                normalized_vector[point] = self.canvas.height / 2 + normalized_vector[point] * -(self.canvas.height / 2)
            print(normalized_vector)

            for point in range(4, len(normalized_vector) - 1, 2):
                normalized_vector[point] = normalized_vector[point] * (self.canvas.width / 2)

            for point in range(5, len(normalized_vector) - 1, 2):
                normalized_vector[point] = normalized_vector[point] * -(self.canvas.width / 2)

            print(normalized_vector)

            def formula(P0, P1, T0, T1, t):
                t2 = t * t
                t3 = t2 * t
                x = (2 * t3 - 3 * t2 + 1) * P0[0] + (t3 - 2 * t2 + t) * T0[0] + (-2 * t3 + 3 * t2) * P1[0] + (t3 - t2) * \
                    T1[0]
                y = (2 * t3 - 3 * t2 + 1) * P0[1] + (t3 - 2 * t2 + t) * T0[1] + (-2 * t3 + 3 * t2) * P1[1] + (t3 - t2) * \
                    T1[1]
                return x, y

            p0_normalized = tuple(normalized_vector[:2])
            p1_normalized = tuple(normalized_vector[2:4])
            t0_normalized = tuple(normalized_vector[4:6])
            t1_normalized = tuple(normalized_vector[6:8])

            for t in range(0, p):
                t_normalized = t / p
                x, y = formula(p0_normalized, p1_normalized, t0_normalized, t1_normalized, t_normalized)
                print(x, y)

                self.canvas.create_line(x, y, x + 1, y + 1, fill="blue", width=2, tags='generated')

            self.canvas.hermite_draws.append([p0, p1, t0, t1, p])
        except ValueError:
            pass

    def generate_results(self):

        if not any([
            len(self.canvas.line_draws) > 0,
            len(self.canvas.hermite_draws) > 0,
            any(len(value) > 0 for value in self.canvas.polygon_draws.values())
        ]):
            return

        fields = list()

        for res in RESOLUTIONS:
            fields.append(Field(res))

        index = 0
        for field in fields:
            for line in self.canvas.line_draws:
                field.add_line(line)

            for polygon_type in self.canvas.polygon_draws.keys():
                if polygon_type == 'Triângulo':
                    for polygon in self.canvas.polygon_draws[polygon_type]:
                        sides = tuple([polygon[1]])
                        field.add_polygon(new_triangle(polygon[0], sides))
                elif polygon_type == 'Quadrado':
                    for polygon in self.canvas.polygon_draws[polygon_type]:
                        field.add_polygon(new_rectangle(polygon[0], polygon[1], polygon[1]))
                elif polygon_type == 'Hexágono':
                    for polygon in self.canvas.polygon_draws[polygon_type]:
                        field.add_polygon(new_hexagon(polygon[0], polygon[1]))

            for curve in self.canvas.hermite_draws:
                field.add_hermite_curve(curve[:-1], curve[-1])

            field_width, field_height = field.resolution
            aspect_ratio = field_width / field_height

            self.tkImages[index] = ImageTk.PhotoImage(field.render().resize((CANVAS_WIDTH, round(CANVAS_HEIGHT / aspect_ratio))))

            self.imageLabelsDict[index].config(image=self.tkImages[index])
            self.imageLabelsDict[index].image = self.tkImages[index]
            index += 1

    def reset_canvas(self):
        index = 0
        for label in self.imageLabelsDict.values():
            resolution = RESOLUTIONS[index]
            aspect_ratio = resolution[0] / resolution[1]

            default_image = f"images\\default.png"
            img = Image.open(default_image).resize(size=(CANVAS_WIDTH, round(CANVAS_HEIGHT / aspect_ratio)))
            self.tkImages[index] = ImageTk.PhotoImage(img)
            label.config(image=self.tkImages[index])
            label.image = self.tkImages[index]

            index += 1

        self.canvas._reset()


class MyCanvas(Canvas):
    def __init__(self, input_frame, input_width, input_height, base_row, base_column):
        self.inputFrame = input_frame
        self.width = input_width
        self.height = input_height
        self.canvas_exist = False
        self.base_row = base_row
        self.base_column = base_column
        self.line_draws = list()
        self.polygon_draws = {'Triângulo': list(), 'Quadrado': list(), 'Hexágono': list()}
        self.hermite_draws = list()

        super().__init__(self.inputFrame, width=self.width, height=self.height, bg='white', borderwidth=0,
                         highlightbackground="black")

        self._generate_canvas(base_row, base_column)

    def _generate_canvas(self, base_row, base_column):
        if self.canvas_exist:
            return

        self.canvas_exist = True

        Label(self.inputFrame, width=15, height=1, background='pink', text='Preview').grid(row=base_row,
                                                                                           column=base_column,
                                                                                           padx=20,
                                                                                           pady=20)

        self.grid(row=base_row + 1, column=base_column)

        assert self.width / 20 == self.width // 20

        x_step = self.width / 20
        y_step = self.height / 20

        for x in np.arange(x_step, self.width, x_step):
            self.create_line(x, 0, x, self.height, fill="gray")

        for y in np.arange(y_step, self.height, y_step):
            self.create_line(0, y, self.width, y, fill="gray")

        self.create_line(0, self.height // 2, self.width, self.height // 2, fill="black", width=2)
        self.create_line(self.width // 2, 0, self.width // 2, self.height, fill="black", width=2)

        self.bind('<Button-1>', self.on_canvas_click)

    def _reset(self):
        self.delete('generated')

        self.line_draws.clear()

        for type in tuple(self.polygon_draws):
            self.polygon_draws[type].clear()

        self.hermite_draws.clear()

    def on_canvas_click(self, event):
        print(event.x, event.y)
        x = (event.x - self.width // 2) / (self.width / 2)
        y = (-(event.y - self.height // 2)) / (self.height / 2)
        print(f"Clicou em ({x}, {y})")


if __name__ == '__main__':
    interface = Interface()
    interface.root.mainloop()
