from ast import literal_eval
from tkinter import *
from PIL import ImageTk, Image
import os

imagelist = sorted([image
                    for image in os.listdir(f"{os.getcwd()}\\images") if
                    image.endswith(".png") and image.startswith('quadrilateral-')],
                   key=lambda item: literal_eval(item.strip('quadrilateral-').split('x')[0]))[:4]


def update_label(label: Label, tkImage: ImageTk):
    label.config(image=tkImage)


def generate_output(masterWindow: Tk = None):
    print(imagelist)

    if masterWindow is None:
        root = Tk()
    else:
        root = masterWindow

    root.title("Imagens geradas")
    root.geometry("1800x1000")
    root.resizable(width=FALSE, height=FALSE)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    outputFrame = Frame(root, width=1500, height=700)
    #    outputFrame.grid_propagate(FALSE)
    outputFrame.grid(row=0, column=0)
    outputFrame.grid_rowconfigure(1, weight=1)
    outputFrame.grid_columnconfigure(1, weight=1)

    upperif = Frame(outputFrame)
    lowerif = Frame(outputFrame)
    upperif.grid(row=0, column=0)
    lowerif.grid(row=2, column=0)

    separator = Frame(outputFrame, width=25, height=25)
    separator.grid(row=1, column=0)

    imageFramesDict = dict()
    textLabelsDict = dict()

    for index in range(0, 4):
        master = upperif if index < 2 else lowerif
        column = index % 2

        imageFramesDict[index] = Frame(master)
        imageFramesDict[index].grid(row=1, column=column)

        textLabelsDict[index] = Label(master,
                                      text=f"{imagelist[index].strip('quadrilateral-').strip('.png')}",
                                      font=('Times New Roman', 15))
        textLabelsDict[index].grid(row=0, column=column)

    imageLabelsDict = dict()
    tkImages = []

    for index, frame in imageFramesDict.items():
        current_image = f"images\\{imagelist[index]}"
        img = Image.open(current_image).resize(size=(400, 400))  # size=(576, 324))
        tkImages.append(ImageTk.PhotoImage(img))
        imageLabelsDict[index] = Label(frame, image=tkImages[index], bg="white")
        imageLabelsDict[index].pack()


    if masterWindow is None:
        root.mainloop()


if __name__ == '__main__':
    generate_output()

