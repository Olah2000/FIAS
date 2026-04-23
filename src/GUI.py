"""
Sebastian Olah    
Muhammad Usman     
Josh Rudnick       
"""


#import face_recognition
import cv2
#import numpy
import tkinter as tk
import PIL.Image
import PIL.ImageTk
#import threading



class GUI:
    """
    Instance method of GUI class.

    Parameters:
        -window:    The main window object
        -image_path:    The path to the image file to be displayed.

    Instance variables:
        -self.window:   An instance of a tk.Tk() (root in main)   
        -self.image_path:   The path to the image file to be displayed
        -self.label:   The tkinter label for displaying the image
        -self.width:   The width of the application window
        -self.height:   The height of the application window

    """
    def __init__(self, window, image_path = "wf/wireframe.png"):
        self.window = window
        self.image_path = image_path
        self.label = None
        self.width = int(window.winfo_screenwidth() / 1.6)
        self.height = int(window.winfo_screenheight() / 1.6)
        self.webcam = WebcamCapture()

        """
        Uploading background image section.

            -self.bimg:     Background image itself
            -self.background_label:     Tkinter label with background to identify it
        """
        self.bgimg = None
        self.background_label = None
        if image_path:
            self.bgimg = BackgroundImage(image_path, self.width, self.height)
            self.background_label = tk.Label(window, image = self.bgimg.get_photo_image())
            self.background_label.place(x = 0, y = 0, relheight = 1, relwidth = 1)



        """
        Setting webcam capture in root window. 

            -self.webcam_label:     Tkinter label for placing the webcam feed inside the root window
            -self.webcam_label.place:   Method for putting the label at a specific position. (A geometry manager, simple so using it here) 
            -self.update_webcam_feed():     Calling the method to update the webcam feed and feed frames

        """
        self.webcam_label = tk.Label(window)
        self.webcam_label.place(relx = 0.5, rely = 0.5, anchor = "center")
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










"""
Class creation of BackgroundImage. Responsible for not only acting as the wireframe for the GUI,
but also is a tkinter Frame widget, so all other main widgets will be attacted to it. (e.g. labels, buttons and webcam capture)
"""
class BackgroundImage:
    
    """
    Instance method of creating BackgroundImage objects. This object is COMPOSED (Not inherited.
    two different things. Better. Establishes more of a 'has-a' relationship whereas inheritance creates a 'is-a' relationship
    Better for this kind of architecture when working with a GUI.
    im rambling. Just initialize the fucking object)
    
    Parameters:
        -image_path:    The path to the background image
        -width:     The width of the background image
        -height:    The height of the background image
    """
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.bgimg = None



        #Error handling in case image loading goes wry
        try:
            self.find_image_path()
            self.load_image()
        except Exception as e:
            print(f"Failed to initialize background image. Error: {e}")



    def find_image_path(self):
        """
        Valides that the image file actually exists
        """
        import os
        if not os.path.exists(self.image_path):
            print(f"Image file not found: {self.image_path}")



    def load_image(self):

        image = PIL.Image.open(self.image_path)
        image = image.resize((int(self.width), int(self.height)))
        self.bgimg = PIL.ImageTk.PhotoImage(image)



    def get_photo_image(self):
        return self.bgimg











class WebcamCapture:
    """
    Instance method of creating a WebcamCapture object. COMPOSED in root window from GUI class (tk.Tk) and will create instant
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