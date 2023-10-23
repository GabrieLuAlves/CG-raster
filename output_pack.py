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


def generate_output():
    print(imagelist)

    root = Tk()
    root.geometry("1800x1000")
    root.resizable(width=FALSE, height=FALSE)

    outputFrame = Frame(root, width=1500, height=700, bg='blue')
    outputFrame.pack_propagate(FALSE)
    outputFrame.pack(expand=True)

    imageFrames = dict()

    upperif = Frame(outputFrame, width=1152, height=324)
    uptext = Frame(outputFrame)
    lowerif = Frame(outputFrame, width=1152, height=324)
    lowtext = Frame(outputFrame)
    upperif.pack(side=TOP)
    uptext.pack(side=TOP)
    lowtext.pack(side=BOTTOM)
    lowerif.pack(side=BOTTOM)

    imageFramesDict = dict()

    for i in range(0, 4):
        imageFramesDict[i] = Frame(upperif if i < 2 else lowerif)
    for frame in imageFramesDict.values():
        frame.pack(side=LEFT)

    imageLabelsDict = dict()
    tkImages = []

    for index, frame in imageFramesDict.items():
        current_image = f"images\\{imagelist[index]}"
        img = Image.open(current_image).resize(size=(576, 324))
        tkImages.append(ImageTk.PhotoImage(img))
        imageLabelsDict[index] = Label(frame, image=tkImages[index], bg="white")
        imageLabelsDict[index].pack()

        textlabel = Label(uptext if index < 2 else lowtext, text=f"{imagelist[index].strip('quadrilateral-').strip('.png')}", bg='red')
        textlabel.pack(side=TOP)

    root.title("Imagens geradas")
    root.mainloop()


if __name__ == '__main__':
    generate_output()

    """
    current_image = f"images\\{imagelist[0]}"
    img = Image.open(current_image)
    tkImage = ImageTk.PhotoImage(img)

    imagelabel = Label(imageframe, text=current_image, image=tkImage, bg="black")

    imgButtonLeft = Image.open('assets\\esquerda.png').resize((75, 75))
    tkImgButtonLeft = ImageTk.PhotoImage(imgButtonLeft)
    imgButtonRight = Image.open('assets\\direita.png').resize((75, 75))
    tkImgButtonRight = ImageTk.PhotoImage(imgButtonRight)

    button1 = Button(root, command=previous_image(label=imagelabel), bg="pink", image=tkImgButtonLeft, width=80, height=100)
    button2 = Button(root,  command=next_image(label=imagelabel), bg="pink", image=tkImgButtonRight, width=80, height=100)

    button1.pack(side=LEFT)
    imageframe.pack(side=LEFT, expand=True)
    button2.pack(side=LEFT)
    imagelabel.pack()
    """
