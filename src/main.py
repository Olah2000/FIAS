import tkinter as tk
from GUI import GUI

if __name__ == "__main__":

    root = tk.Tk()      #Create Tkinter window

    FIAS = GUI(root)    #Initialize the GUI

    root.after(10, FIAS.update_webcam_feed)     #Wait, then start updating webcam feed

    def on_app_close():
        """
        Method that handles exiting the program and makes sure that all is done neatly.
        """
        FIAS.stop_feed()
        FIAS.webcam.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_app_close)     #When the user tries to close the window, starts  shutdown activies in GUI

    root.mainloop()     #End Tkinter window


