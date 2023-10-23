from ast import literal_eval
from tkinter import *
from PIL import ImageTk, Image
import os

imagelist = sorted([image
                    for image in os.listdir(f"{os.getcwd()}\\images") if image.endswith(".png") and image.startswith('quadrilateral-')],
                   key=lambda item: f"{literal_eval(item.strip('quadrilateral-').split('x')[0])}")


def previous_image(**kwargs):
    def function(label=kwargs['label']):
        print('CLICOU', imagelist)
        print('TEXTO ANTES', label.cget('text'))

        if label.cget('text') == 'images\\' + imagelist[0]:
            print('FOI 1')
            return

        new_image = imagelist[imagelist.index(label.cget('text').split('images\\')[1]) - 1]
        img = Image.open('images\\' + new_image)
        tkImage = ImageTk.PhotoImage(img)

        label.configure(image=tkImage, text='images\\'+new_image)
        label.image = tkImage
        label.pack()
        print("TEXTO DEPOIS", label.cget('text'))

    return function


def next_image(**kwargs):
    def function(label: Label = kwargs['label']):
        print('CLICOU', imagelist)
        print('TEXTO ANTES', label.cget('text'))

        if label.cget('text') == 'images\\' + imagelist[-1]:
            print('FOI 2')
            return

        new_image = imagelist[imagelist.index(label.cget('text').split('images\\')[1]) + 1]
        img = Image.open('images\\' + new_image)
        tkImage = ImageTk.PhotoImage(img)

        label.configure(image=tkImage, text='images\\'+new_image)
        label.image = tkImage
        label.pack()
        print("TEXTO DEPOIS", label.cget('text'))

    return function


if __name__ == '__main__':

    root = Tk()
    root.geometry("1300x750")

    #frames = {resolution.strip(".png"): Frame(root) for resolution in imagelist}
    #print(frames)

    print(imagelist)

    imageframe = Frame(root , width=1300, height=800)

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

    root.mainloop()
