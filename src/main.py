
import multiprocessing      #Adds functionality for making the program utilize another code for face rec compute
import tkinter as tk        #Window and GUI implementation
import numpy as np
from GUI import GUI, WEBCAM_FRAME_DELAY_MS
from frcontroller import FRC        



if __name__ == "__main__":

    multiprocessing.freeze_support()        #Essential call for using multiprocess and explicity documented to be called after __name == "__main__"

    root = tk.Tk(className = " FIAS")   #Create Tkinter window. Yes, the space there is intentional DON'T TOUCH IT!!! (it makes the 'f' in FIAS lowercase for some reason)
    
    root.resizable(False, False)

    FIAS = GUI(root)        #Initialize the GUI
    controller = FRC()      #Initialize the face recognition controller
    controller.start()      #Spawn proces of controller (FRC)



    def update_fs_loop():
        if FIAS.webcam is None:
            root.after(WEBCAM_FRAME_DELAY_MS, update_fs_loop)
            return

        pil_frame = FIAS.webcam.get_frame_image()


        if pil_frame is not None:
            rgb_frame = np.array(pil_frame)         # convert to numpy for face recognition
            controller.update_frame(rgb_frame)
            results = controller.get_results()
            FIAS.display_overlays(results, pil_frame)
            FIAS.display_status(results)
            
        root.after(WEBCAM_FRAME_DELAY_MS,   update_fs_loop)

    

    """
    Help to application to start 493009458 hours after you run it

    """

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


