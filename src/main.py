import tkinter as tk
from GUI import GUI, WEBCAM_FRAME_DELAY_MS
from frcontroller import FRC



if __name__ == "__main__":

    root = tk.Tk(className = " FIAS")   #Create Tkinter window. Yes, the space there is intentional DON'T TOUCH IT!!! (it makes the 'f' in FIAS lowercase for some reason)

    FIAS = GUI(root)    #Initialize the GUI
    controller = FRC()
    controller.start()

    def update_fs_loop():
        rgb_frame = FIAS.webcam.get_frame_rgb()
        if rgb_frame is not None:
            
            controller.update_frame(rgb_frame)
            results = controller.get_results()
            FIAS.display_overlays(results)
            FIAS.display_status(results)
        root.after(WEBCAM_FRAME_DELAY_MS, update_fs_loop)


    root.after(10, update_fs_loop)



    def on_app_close():
        """
        Method that handles exiting the program and makes sure that all is done neatly.
        """
        controller.stop()
        FIAS.stop_feed()
        FIAS.webcam.cleanup()
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_app_close)     #When the user tries to close the window, starts  shutdown activies in GUI

    root.mainloop()     #End Tkinter window


