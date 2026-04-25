"""
Sebastian Olah    
Muhammad Usman     
Josh Rudnick       
"""


import cv2
import tkinter as tk
from tkinter import messagebox
import PIL.Image
import PIL.ImageTk
import PIL.ImageDraw
import PIL.ImageFont


"""
Constants here for seating GUI elements nicely 
"""
WINDOW_SCALE_FACTOR = 1.6
WEBCAM_SCALE_FACTOR = 1.2
WEBCAM_FRAME_DELAY_MS = 33 #This is about 30 fps






















class GUI:
    """
    Instance method of GUI class.

    Parameters:
        -window:    The main window object
        -image_path:    The path to the background image file to be displayed.

    Instance variables:
        -self.window:   An instance of a tk.Tk() (root in main)
        -self.image_path:   The path to the background image file to be displayed
        -self.bimg:     Background image itself
        -self.background_label:     Tkinter label widget with background to identify it
        -self.width:   The width of the application window
        -self.height:   The height of the application window
        -self.running:  Flag for neat shutdown operations
        -self.webcam:   Composed instance of WebcamCapture class inside GUI class.
    """
    def __init__(self, window, image_path = "wf/wireframe.png"):
        self.window = window
        self.image_path = image_path
        self.bgimg = None
        self.background_label = None
        self.width = int(window.winfo_screenwidth() / WINDOW_SCALE_FACTOR)
        self.height = int(window.winfo_screenheight() / WINDOW_SCALE_FACTOR)
        self.running = True
        self.webcam = WebcamCapture()



        """
        Uploading background image section. Composes BackgrounImage in GUI with these lines.
        bgimg is initialized as a BackgroundImage object w all properties, tkinter label is created, and is placed
        """
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



        self.status_label = tk.Label(window, text = "No face detected", font = ("JetBrains Mono", 12), bg = "white", fg = "black")
        self.status_label.place(relx = 0.5, rely = 0.9, anchor = "center")


        
        self.set_window_size()  #Organizes everything after initialized in



    def set_window_size(self):
        """
        This method sets the size of the application to the 1/6th of the users resolution
        """
        try:
            self.window.geometry(f"{self.width}x{self.height}")
        except Exception as e:
            raise RuntimeError(f"Could not find usable resolution. Error: {e}")




    def display_overlays(self, results):
        """
        Method for creating the display for the facial_recognition elements that will
        signal users if faces match, don', etc. 
        """
        frame = self.webcam.get_frame_image()
        if frame is None:
            return
        
        draw = PIL.ImageDraw.Draw(frame)

        for result in results:
            top, right, bottom, left = result["location"]
            name = result["name"]
            confidence = result["confidence"]

            if name == "Unknown Student":
                color = "red"
            else:
                color = "green"

            draw.rectangle([left, top, right, bottom], outline = color, width = 2)
            draw.text((left, top), f"{name}: {confidence:.2f}", fill = "black")

        photo = PIL.ImageTk.PhotoImage(frame)
        self.webcam_label.config(image = photo)
        self.webcam_label.image = photo



    def display_status(self, results):
        """
        Method that actually handles the status label based on recognition results
        """
        if not results:
            message = "No face detected"
        elif any(r["name"] == "Unknown Student" for r in results):
            message = "Unknown student detected"
        else:
            names = [r["name"] for r in results]
            message = f"Recognized: {', '.join(names)}"

        self.status_label.config(text = message)

    

    def stop_feed(self):
        """
        Flag raiser to stop feed instnatly when user closes application
        """
        self.running = False






























class BackgroundImage:
    """
    Instance method of creating BackgroundImage objects. This object is COMPOSED (Not inherited.
    two different things. Better. Establishes more of a 'has-a' relationship whereas inheritance creates a 'is-a' relationship
    Better for this kind of architecture when working with a GUI.
    im rambling. Just initialize the fucking object)
    
    Parameters:
        -self.image_path:    The path to the background image
        -self.width:     The width of the background image
        -self.height:    The height of the background image
        -self.bgimg:    
    """
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.bgimg = None



        #Error handling in case image loading goes awry
        try:
            self.validate_image_path()
            self.load_image()
        except Exception as e:
            print(f"Failed to initialize background image. Error: {e}")



    def validate_image_path(self):
        """
        Valides that the image file actually exists. Lazy imports os to save startup performance
        """
        import os
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image file not found: {self.image_path}")



    def load_image(self):
        """
        Method for opening image with Pillow, resizing, then making it PILTk and initalization variable.
        'image' is a local variable to hold the PIL Image object, and then becomes 'self.bgimg' and turned into tkinter widget
        """
        image = PIL.Image.open(self.image_path)
        image = image.resize((int(self.width), int(self.height)))
        self.bgimg = PIL.ImageTk.PhotoImage(image)



    def get_photo_image(self):
        """
        Helper function to retrieve the background image of the GUI
        """
        return self.bgimg




























class WebcamCapture:
    """
    Instance method of creating a WebcamCapture object. COMPOSED in root window from GUI class (tk.Tk) and will create instant
    webcam capture

    Initialization variables:
        -self.width:    width of webcam feed object
         -self.height:   height of webcam feed object
         -self.vcap:     Instance of webcam feed object
    """
    def __init__(self):
        self.width = 640
        self.height = 480

        #Create actual webcam feed with set dimensions ^^^
        self.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)      #Grab default camera
        self.vcap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.width / WEBCAM_SCALE_FACTOR))      
        self.vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.height / WEBCAM_SCALE_FACTOR))



    def get_frame_rgb(self):
        """
        Method for capturing single frame from webcam object. This is the raw frame that will be used for the facial_recognition module
        because methods in that module expect a numpy array only, whereas PIL.Images are separate

        Returns:
            -frame:     The captured frame from the webcam held as numpy array
        """        
        _, frame = self.vcap.read()
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    


    def get_frame_image(self):
        """
        Method for converting the captured frame to a PIL Image. This is used for the GUI only and can't be used for any
        kind of data processing
        """
        rgbframe = self.get_frame_rgb()
        if rgbframe is None:
            return None
        return PIL.Image.fromarray(rgbframe)
    


    def cleanup(self):
        """
        Cleanup method that should be called whenever the webcam capture is no longer needed
        """
        if self.vcap.isOpened():
            self.vcap.release()