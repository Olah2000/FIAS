"""
Sebastian Olah
Muhammad Usman
Josh Rudnick

UML Diagram Assignment
CSIII
Mr.Ding

Starter code for GUI
"""

# Modules (Just for now importing entire module. Will change in later sessions)
import face_recognition
import cv2
import numpy
import tkinter as tk
import PIL.Image
import PIL.ImageTk
from threading import *



# Class creation of GUI interface
class GUI:

    """
    Instance method of GUI class.
    
    Parameters:
        -self:      The instance of the GUI class
        -window:    The main window object
        -image_path:    The path to the image file to be displayed
    """
    def __init__(self, window, image_path = None):
        self.window = window
        self.image_path = image_path
        self.label = None
        self.width = window.winfo_screenwidth() // 1.06
        self.height = window.winfo_screenheight() // 1.06
        self.webcam = WebcamCapture()
        self.webcam_label = tk.Label(window)
        self.webcam_label.pack()
        self.update_webcam_feed()



    """
    Method for updating the webcam feed inside the label widget. Uses 
    after() method to make sure the GUI isn't inhibited
    """
    def update_webcam_feed(self):

        try:

            ret, frame = self.webcam.cap_frame()

            if ret:
                #Convert frame to PIL Image and Tkinter PhotoImage
                frame = PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                hungFrame = PIL.ImageTk.PhotoImage(frame)

                #Update the labale that capture will be apart of
                self.webcam_label.config(image = hungFrame)
                self.webcam_label.frame = hungFrame

                #Buffer next update. First paramater that's an int is ms of buf. 33ms ~ 30 FPS
                self.window.after(33, self.update_webcam_feed)

        except Exception as e:
            print(f"Failed to initialize webcam feed. Make sure the webcam is connected and accessible. Error: {e}")



    """
    This method sets the size of the application to the max
    size of the users resoultion

    Parameters:
        -self       The instance of the GUI class
    Returns:
        -None
    """
    def set_geom(self):

        try:
    
            self.window.geometry(f"{self.width}x{self.height}")

        except Exception as e:
            print(f"Could not find usable resoultion. Error: {e}")



class BackgroundImage:
    pass



"""
Class creation of WebcamCapture. Child of GUI, because the webcam 'widget' will go off
elements that reside in the GUI parent class. Elements like the root window resoultion.
"""
class WebcamCapture:
    
    """
    Instance method of creating a WebcamCapture object. Inherits root window from GUI parent class (tk.Tk) and will create instant
    webcam capture
    """
    def __init__(self):
        
        #Set dimensions of webcam feed object that come from the root windows (GUI parent class) 
        self.width = 640
        self.height = 480

        #Create actual webcam feed with set dimensions ^^^
        self. vcap = cv2.VideoCapture(0)      #Grab default camera
        self. vcap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width * 1.2)      
        self.vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height * 1.2)



    """
    Method for capturing single frame from webcam object

    Parameters:
        -self:      The instance of the WebcamCapture class
    Returns:
        -frame:     The captured frame from the webcam held as numpy array
        -ret:       A boolean indicating whether the frame was captured successfully
    """
    def cap_frame(self):
        
        return self.vcap.read()
    


    """
    Cleanup method that should be called whenever the webcam capture is no longer needed
    """
    def cleanup(self):
        self.vcap.release()