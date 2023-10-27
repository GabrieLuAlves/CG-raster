from ast import literal_eval
from math import cos, sin, sqrt, pi
from tkinter import *

import numpy as np
from PIL import ImageTk, Image
import os

ROOT_WIDTH = 1900
ROOT_HEIGHT = 1000
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400

imagelist = sorted([image
                    for image in os.listdir(f"{os.getcwd()}\\images") if
                    image.endswith(".png") and image.startswith('quadrilateral-')],
                   key=lambda item: literal_eval(item.strip('quadrilateral-').split('x')[0]))[:4]


class Interface:
    def __init__(self):
        print(imagelist)

        self.root = Tk()

        self.root.title("Imagens geradas")
        self.root.geometry(f"{ROOT_WIDTH}x{ROOT_HEIGHT}")
        self.root.resizable(width=FALSE, height=FALSE)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.outputFrame = Frame(self.root, width=1500, height=850)
        self.outputFrame.grid_propagate(FALSE)
        self.outputFrame.grid(row=0, column=0)
        self.outputFrame.grid_rowconfigure(1, weight=1)
        self.outputFrame.grid_columnconfigure(1, weight=1, minsize=900)

        upperif = Frame(self.outputFrame)
        lowerif = Frame(self.outputFrame)
        upperif.grid(row=0, column=1)
        lowerif.grid(row=2, column=1)

        separator = Frame(self.outputFrame, width=25, height=25)
        separator.grid(row=1, column=0)

        self.imageFramesDict = dict()
        self.textLabelsDict = dict()

        for index in range(0, 4):
            master = upperif if index < 2 else lowerif
            column = index % 2

            self.imageFramesDict[index] = Frame(master)
            self.imageFramesDict[index].grid(row=1, column=column)

            self.textLabelsDict[index] = Label(master,
                                               text=f"{imagelist[index].strip('quadrilateral-').strip('.png')}",
                                               font=('Times New Roman', 15))
            self.textLabelsDict[index].grid(row=0, column=column)

        self.imageLabelsDict = dict()
        self.tkImages = []

        for index, frame in self.imageFramesDict.items():
            current_image = f"images\\{imagelist[index]}"
            img = Image.open(current_image).resize(size=(400, 400))  # size=(576, 324))
            self.tkImages.append(ImageTk.PhotoImage(img))
            self.imageLabelsDict[index] = Label(frame, image=self.tkImages[index], bg="white")
            self.imageLabelsDict[index].pack()

        self.inputFrame = Frame(self.root, width=800, height=ROOT_HEIGHT)
        self.inputFrame.grid_propagate(FALSE)
        self.inputFrame.grid(row=0, column=1)
        self.inputFrame.columnconfigure(1, minsize=800)

        self.generate_line_input(0)

        self._currentPolygonOption = None
        self.generate_polygon_input(2)

        self.canvas = MyCanvas(self.inputFrame, CANVAS_WIDTH, CANVAS_HEIGHT)
    def generate_line_input(self, base_row):
        Label(self.inputFrame, width=15, height=1, background='pink', text='Adicionar linha').grid(row=base_row,
                                                                                                   column=0,
                                                                                                   padx=20,
                                                                                                   pady=20)
        lineInputFrame = Frame(self.inputFrame)
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

    def generate_polygon_input(self, base_row):
        Label(self.inputFrame, width=15, height=1, background='pink', text='Adicionar Poligono').grid(row=base_row,
                                                                                                      column=0,
                                                                                                      padx=20,
                                                                                                      pady=20)
        self.polygonInputFrame = Frame(self.inputFrame)
        self.polygonInputFrame.grid(row=base_row + 1, column=0, sticky='w')

        Label(self.polygonInputFrame, text='Escolha o polígono:').grid(row=1, column=0)

        options = ('Triângulo', 'Quadrado', 'Hexágono')
        self._selectedOption = StringVar()
        self._selectedOption.set(options[0])

        self.polygonsDropdown = OptionMenu(self.polygonInputFrame, self._selectedOption, *options)
        self.polygonsDropdown.grid(row=1, column=1)

        if self._selectedOption.get() == self._currentPolygonOption:
            return

        if hasattr(self, 'currentPolygonInput'):
            self.currentPolygonInput.destroy()

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

    def _add_polygon(self, dropdown=None, option=None, mode=None):
        # FIXME INTEGRAR A API
        print(self._selectedOption.get())

        list_of_dots = []
        try:
            for entry in self.polygonInputEntryList:
                value = float(entry.get().strip())
                if not -1 <= value <= 1:
                    raise ValueError

                list_of_dots.append(float(entry.get()))
                entry.delete(0, END)

            if not list_of_dots[-1] > 0:
                raise ValueError

            vertices = list()

            if self._selectedOption.get() == 'Triângulo':

                center_x = self.canvas.width / 2 + (list_of_dots[0] * (self.canvas.width / 2))
                center_y = self.canvas.height / 2 + (list_of_dots[1] * -(self.canvas.width / 2))

                x1 = center_x - ((list_of_dots[2] * self.canvas.width) / 2)
                y1 = center_y + (((sqrt(3) / 2) * list_of_dots[2] * self.canvas.width) / 2)
                x2 = center_x
                y2 = center_y + (((sqrt(3) / 2) * list_of_dots[2] * -self.canvas.width) / 2)
                x3 = center_x + ((list_of_dots[2] * self.canvas.width) / 2)
                y3 = y1

                vertices = [x1, y1, x2, y2, x3, y3]

                self.canvas.draws.append(self.canvas.create_polygon(vertices, fill="green", width=1))

            elif self._selectedOption.get() == 'Quadrado':

                center_x = self.canvas.width / 2 + (list_of_dots[0] * (self.canvas.width / 2))
                center_y = self.canvas.height / 2 + (list_of_dots[1] * -(self.canvas.width / 2))

                x1 = center_x - (list_of_dots[2] * self.canvas.width / 2)
                y1 = center_y - (list_of_dots[2] * -(self.canvas.width / 2))
                x2 = center_x + (list_of_dots[2] * self.canvas.width / 2)
                y2 = center_y + (list_of_dots[2] * -(self.canvas.width / 2))

                vertices = [x1, y1, x2, y2]

                self.canvas.draws.append(self.canvas.create_rectangle(vertices, fill='yellow', width=1))

            elif self._selectedOption.get() == 'Hexágono':
                for i in range(6):
                    angle = 2 * pi / 6 * i
                    x = (list_of_dots[0] + 2 * list_of_dots[2] * cos(angle)) * (self.canvas.width / 2)
                    y = (list_of_dots[1] + 2 * list_of_dots[2] * sin(angle)) * (-self.canvas.height / 2)
                    x += (self.canvas.width / 2)
                    y += (self.canvas.height / 2)
                    vertices.extend((x, y))

                self.canvas.draws.append(self.canvas.create_polygon(vertices, fill='blue', width=1))
        except ValueError:
            pass

    def _add_line(self):
        # FIXME INTEGRAR A API

        list_of_dots = []
        try:
            for entry in self.lineInputEntryList:
                value = float(entry.get().strip())
                if not -1 <= value <= 1:
                    raise ValueError

                list_of_dots.append(float(entry.get()))
                entry.delete(0, END)

            print(list_of_dots)

            self.canvas.draws.append(self.canvas.create_line(
                self.canvas.width // 2 + (list_of_dots[0] * (self.canvas.width // 2)),
                self.canvas.height // 2 + (list_of_dots[1] * -(self.canvas.width // 2)),
                self.canvas.width // 2 + (list_of_dots[2] * (self.canvas.width // 2)),
                self.canvas.height // 2 + (list_of_dots[3] * -(self.canvas.width // 2)),
                fill='red',
                width=1))

        except ValueError:
            pass


class MyCanvas(Canvas):
    def __init__(self, input_frame, input_width, input_height):
        self.inputFrame = input_frame
        self.width = input_width
        self.height = input_height
        self.canvas_exist = False
        self.draws = list()

        super().__init__(self.inputFrame, width=self.width, height=self.height, bg='white', borderwidth=0,
                         highlightbackground="black")

        self._generate_canvas()

    def _generate_canvas(self):
        if self.canvas_exist:
            return

        self.canvas_exist = True

        Label(self.inputFrame, width=15, height=1, background='pink', text='Preview').grid(row=4, column=0, padx=20,
                                                                                           pady=20)

        self.grid(row=5, column=0)
        self.grid_propagate(FALSE)

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
        # self.scale("all", self.width // 2, self.height // 2, 1, -1)

        self.reset_button = Button(self.inputFrame, text='Reset', command=self.reset)
        self.reset_button.grid(row=6, column=0, pady=(10, 0))

    def reset(self):
        for draw in self.draws:
            self.delete(draw)

    def on_canvas_click(self, event):
        print(event.x, event.y)
        x = (event.x - self.width // 2) / (self.width / 2)
        y = (-(event.y - self.height // 2)) / (self.height / 2)
        print(f"Clicou em ({x}, {y})")


def update_image(label: Label, tkImage: ImageTk):
    label.config(image=tkImage)


def generate_hermite_input():
    pass


if __name__ == '__main__':
    interface = Interface()
    interface.root.mainloop()
