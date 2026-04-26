
import multiprocessing      #Adds functionality for making the program utilize another code for face rec compute
import tkinter as tk        #Window and GUI implementation
from GUI import GUI, WEBCAM_FRAME_DELAY_MS
from frcontroller import FRC        



if __name__ == "__main__":

    #
    multiprocessing.freeze_support()

    root = tk.Tk(className = " FIAS")   #Create Tkinter window. Yes, the space there is intentional DON'T TOUCH IT!!! (it makes the 'f' in FIAS lowercase for some reason)

    FIAS = GUI(root)        #Initialize the GUI
    controller = FRC()      #Initialize the face recognition controller
    controller.start()      #Spawn proces of controller (FRC)

    def update_fs_loop():
        """
        Method for refreshing the internal face recognition processes. Interestingly, it calls itself recursively at the end.
        Making sure that each frame is checked,
        """
        rgb_frame = FIAS.webcam.get_frame_rgb()
        if rgb_frame is not None:
            
            controller.update_frame(rgb_frame)
            results = controller.get_results()
            FIAS.display_overlays(results)
            FIAS.display_status(results)
        root.after(WEBCAM_FRAME_DELAY_MS, update_fs_loop)

    root.after(10, FIAS.start_webcam)
    root.after(100, update_fs_loop)



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


