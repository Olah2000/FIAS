from tkinter import *
import cv2
from threading import *

def window_Tk():
    root = Tk()
    root.geometry('200x200')
    btn = Button(root, text='click').pack()
    root.mainloop()

def window_CV():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty('frame',1) == -1 :
            break
    cap.release()
    cv2.destroyAllWindows()

t1 = Thread(target=window_Tk)
t2 = Thread(target=window_CV)

t1.start()
t2.start()