import tkinter
from math import cos, sin, sqrt, pi

from PIL import ImageTk, Image
from tkinter import Button,END, Entry, FALSE, Frame, Label, OptionMenu, Scrollbar, StringVar, Tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from raster import Field, new_triangle, new_hexagon, new_rectangle

ROOT_WIDTH = 1900
ROOT_HEIGHT = 1000
OUTPUT_WIDTH = 400
INPUT_HEIGHT = 400
CANVAS_WIDTH = 4
CANVAS_HEIGHT = 4
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
            img = Image.open(current_image).resize(size=(OUTPUT_WIDTH, round(INPUT_HEIGHT / aspect_ratio)))
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

        self.canvas = MyCanvas(previewFrame, 0, 1)

        buttonsFrames = Frame(previewFrame)
        buttonsFrames.grid(row=2, column=1)

        self.reset_button = Button(buttonsFrames, text='Reset', command=self.reset_canvas)
        self.reset_button.grid(row=0, column=0, pady=(10, 0), padx=(0, 10))

        self.results_button = Button(buttonsFrames, text='Gerar Resultados', command=self.generate_results)
        self.results_button.grid(row=0, column=1, pady=(10, 0), padx=(0, 10))

        Label(inputFrame, text="Pontos inseridos:").grid(row=1, column=0)
        self.inputListLabel = tkinter.Text(inputFrame, width=55, height=15, wrap='word')

        text = (
            f"Linhas: {self.canvas.line_draws}\n"
            f"\n"
            f"Triângulos: {self.canvas.polygon_draws['Triângulo']['output']}\n"
            f"Quadrados: {self.canvas.polygon_draws['Quadrado']['output']}\n"
            f"Hexágonos: {self.canvas.polygon_draws['Hexágono']['output']}\n"
            f"\n"
            f"Linhas de Hermite: {self.canvas.hermite_draws}\n")

        self.inputListLabel.insert('1.0', text)
        self.inputListLabel.grid(row=2, column=0)
        self.inputListLabel.columnconfigure(0, minsize=360)
        self.inputListLabel.config(state='disabled')

        scrollbar = Scrollbar(self.inputListLabel, orient='vertical', command=self.inputListLabel.yview)
        self.inputListLabel.config(yscrollcommand=scrollbar.set)

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

        try:
            list_of_points = [float(element.get().strip()) for element in self.lineInputEntryList]

            if not all(
                    [
                        all(-1 <= element <= 1 for element in list_of_points),
                        list_of_points not in self.canvas.line_draws
                    ]):
                raise ValueError

            for entry in self.lineInputEntryList:
                entry.delete(0, END)

            p1 = tuple(list_of_points[:2])
            p2 = tuple(list_of_points[2:])

            if (p1, p2) in self.canvas.line_draws:
                raise ValueError
            line, = plt.plot((p1[0], p2[0]), [p1[1], p2[1]], color='red', linewidth=1)

            self.canvas.draw()
            self.canvas.line_draws.append([p1, p2])
            self.canvas.draws.append(line)
            self.update_input_list()

        except ValueError:
            pass

    def _add_polygon(self, dropdown=None, option=None, mode=None):

        try:
            list_of_points = []

            x = float(self.polygonInputEntryList[0].get().strip())
            y = float(self.polygonInputEntryList[1].get().strip())
            p = float(self.polygonInputEntryList[2].get().strip())

            if not all(
                    [-1 <= x <= 1,
                     -1 <= y <= 1,
                     0 < p <= 2,
                     tuple((tuple((x, y)), p)) not in
                          self.canvas.polygon_draws[self._selectedOption.get()]['input']]):
                raise ValueError

            for entry in self.polygonInputEntryList:
                list_of_points.append(float(entry.get().strip()))
                entry.delete(0, END)

            x, y = [], []
            color = str()

            if self._selectedOption.get() == 'Triângulo':

                center_x = list_of_points[0]
                center_y = list_of_points[1]
                half_side = list_of_points[2] / 2
                height = half_side * sqrt(3)

                x1 = center_x - half_side
                y1 = center_y - height / 2
                x2 = center_x
                y2 = center_y + height / 2
                x3 = center_x + half_side
                y3 = y1

                x.extend((x1, x2, x3, x1))
                y.extend((y1, y2, y3, y1))

                color = 'green'

            elif self._selectedOption.get() == 'Quadrado':

                center_x = list_of_points[0]
                center_y = list_of_points[1]
                half_side = list_of_points[2] / 2

                x1 = center_x - half_side
                y1 = center_y + half_side
                x2 = center_x + half_side
                y2 = center_y + half_side
                x3 = center_x + half_side
                y3 = center_y - half_side
                x4 = center_x - half_side
                y4 = center_y - half_side

                x.extend((x1, x2, x3, x4, x1))
                y.extend((y1, y2, y3, y4, y1))

                color = 'yellow'

            elif self._selectedOption.get() == 'Hexágono':
                for i in range(6):
                    angle = 2 * pi / 6 * i
                    px = (list_of_points[0] + list_of_points[2] * cos(angle))
                    py = (list_of_points[1] + list_of_points[2] * sin(angle))

                    x.append(px)
                    y.append(py)

                color = 'purple'

            else:
                return

            polygon, = plt.fill(x, y, color=color, linewidth=1, alpha=0.9)

            temp = []
            self.canvas.draw()
            self.canvas.polygon_draws[self._selectedOption.get()]['input'].append((
                tuple(list_of_points[:2]),
                list_of_points[2]))
            for px, py in zip(x[:-1], y[:-1]):
                temp.append((px, py))
            self.canvas.polygon_draws[self._selectedOption.get()]['output'].append(temp)
            self.canvas.draws.append(polygon)
            self.update_input_list()

        except ValueError:
            pass

    def _add_hermite_curve(self):
        try:
            list_of_points = [float(entry.get().strip()) for entry in self.hermiteInputEntryList]
            if not all(
                    [
                        -1 <= list_of_points[0] <= 1,
                        -1 <= list_of_points[1] <= 1,
                        -1 <= list_of_points[2] <= 1,
                        -1 <= list_of_points[3] <= 1,
                        0 < list_of_points[8],
                    ]
            ):
                raise ValueError

            for entry in self.hermiteInputEntryList:
                entry.delete(0, END)

            p0 = tuple(list_of_points[:2])
            p1 = tuple(list_of_points[2:4])
            t0 = tuple(list_of_points[4:6])
            t1 = tuple(list_of_points[6:8])
            p = int(list_of_points[-1])

            t = np.linspace(0, 1, p)

            x = (2 * t ** 3 - 3 * t ** 2 + 1) * p0[0] + (t ** 3 - 2 * t ** 2 + t) * t0[0] + (
                        -2 * t ** 3 + 3 * t ** 2) * p1[0] + (t ** 3 - t ** 2) * t1[0]
            y = (2 * t ** 3 - 3 * t ** 2 + 1) * p0[1] + (t ** 3 - 2 * t ** 2 + t) * t0[1] + (
                        -2 * t ** 3 + 3 * t ** 2) * p1[1] + (t ** 3 - t ** 2) * t1[1]

            hermite_curve, = plt.plot(x, y, color='blue', linewidth=1)

            self.canvas.draw()
            self.canvas.hermite_draws.append([p0, p1, t0, t1, p])
            self.canvas.draws.append(hermite_curve)
            self.update_input_list()

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
                    for polygon in self.canvas.polygon_draws[polygon_type]['input']:
                        sides = tuple([polygon[1]])
                        field.add_polygon(new_triangle(polygon[0], sides))
                elif polygon_type == 'Quadrado':
                    for polygon in self.canvas.polygon_draws[polygon_type]['input']:
                        field.add_polygon(new_rectangle(polygon[0], polygon[1], polygon[1]))
                elif polygon_type == 'Hexágono':
                    for polygon in self.canvas.polygon_draws[polygon_type]['input']:
                        field.add_polygon(new_hexagon(polygon[0], polygon[1]))

            for curve in self.canvas.hermite_draws:
                field.add_hermite_curve(curve[:-1], curve[-1])

            field_width, field_height = field.resolution
            aspect_ratio = field_width / field_height

            self.tkImages[index] = ImageTk.PhotoImage(
                field.render().resize((OUTPUT_WIDTH, round(INPUT_HEIGHT / aspect_ratio))))

            self.imageLabelsDict[index].config(image=self.tkImages[index])
            self.imageLabelsDict[index].image = self.tkImages[index]
            index += 1

    def update_input_list(self):
        self.inputListLabel.config(state='normal')
        self.inputListLabel.delete('1.0', 'end')

        text = (f"Linhas: {self.canvas.line_draws}\n"
                f"\n"
                f"Triângulos: {self.canvas.polygon_draws['Triângulo']['output']}\n"
                f"Quadrados: {self.canvas.polygon_draws['Quadrado']['output']}\n"
                f"Hexágonos: {self.canvas.polygon_draws['Hexágono']['output']}\n"
                f"\n"
                f"Linhas de Hermite: {self.canvas.hermite_draws}\n"
                )

        self.inputListLabel.insert('1.0', text)
        self.inputListLabel.config(state='disabled')

    def reset_canvas(self):
        index = 0
        for label in self.imageLabelsDict.values():
            resolution = RESOLUTIONS[index]
            aspect_ratio = resolution[0] / resolution[1]

            default_image = f"images/default.png"
            img = Image.open(default_image).resize(size=(OUTPUT_WIDTH, round(INPUT_HEIGHT / aspect_ratio)))
            self.tkImages[index] = ImageTk.PhotoImage(img)
            label.config(image=self.tkImages[index])
            label.image = self.tkImages[index]

            index += 1

        self.canvas._reset()
        self.update_input_list()


class MyCanvas(FigureCanvasTkAgg):
    def __init__(self, input_frame, base_row, base_column):
        self.inputFrame = input_frame
        self.canvas_exist = False
        self.base_row = base_row
        self.base_column = base_column
        self.line_draws = list()
        self.polygon_draws = {'Triângulo': {'input': list(), 'output': list()},
                              'Quadrado': {'input': list(), 'output': list()},
                              'Hexágono': {'input': list(), 'output': list()}}
        self.hermite_draws = list()
        self.draws = list()

        plt.figure(figsize=(CANVAS_WIDTH, CANVAS_HEIGHT))

        plt.title('Espaço normalizado')

        plt.xlim(-1.01, 1.01)
        plt.ylim(-1.01, 1.01)

        super().__init__(plt.gcf(), master=self.inputFrame)

        self._generate_canvas(base_row, base_column)

    def _generate_canvas(self, base_row, base_column):
        if self.canvas_exist:
            return

        self.canvas_exist = True

        Label(self.inputFrame, width=15, height=1, background='pink', text='Preview').grid(row=base_row,
                                                                                           column=base_column,
                                                                                           padx=20,
                                                                                           pady=20)

        self.get_tk_widget().grid(row=base_row + 1, column=base_column)

    def _reset(self):
        for polygon_type in tuple(self.polygon_draws):
            for mode in ('input', 'output'):
                self.polygon_draws[polygon_type][mode].clear()

        for draw in self.draws:
            draw.remove()

        self.draws.clear()
        self.line_draws.clear()
        self.hermite_draws.clear()
        self.draw()


if __name__ == '__main__':
    interface = Interface()
    interface.root.mainloop()
