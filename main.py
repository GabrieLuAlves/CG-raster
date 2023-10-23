from ast import literal_eval
from tkinter import *
from PIL import ImageTk, Image
import os
from output_grid import generate_output

imagelist = sorted([image
                    for image in os.listdir(f"{os.getcwd()}\\images") if image.endswith(".png") and image.startswith('quadrilateral-')],
                   key=lambda item: f"{literal_eval(item.strip('quadrilateral-').split('x')[0])}")


if __name__ == '__main__':

    root = Tk()
    root.geometry("1300x750")
    root.resizable(width=FALSE, height=FALSE)

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
    button2 = Button(root,  command=generate_output, bg="pink", image=tkImgButtonRight, width=80, height=100)
    imagelabel.pack()

    root.mainloop()
