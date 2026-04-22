import tkinter as tk
from GUI import *

if __name__ == "__main__":

    root = tk.Tk()

    FIAS = GUI(root)

    FIAS.set_geom()

    root.mainloop()

    FIAS.webcam.cleanup()

    pass
