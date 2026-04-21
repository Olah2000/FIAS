import tkinter as tk
from GUI import *

if __name__ == "__main__":

    root = tk.Tk()

    FIAS = GUI(root)

    FIASWEBCAM = WebcamFeed(root)

    FIAS.set_geom()

    root.mainloop()

    pass
