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
        self.canvas = None
        self.width = window.winfo_screenwidth() // 1.5
        self.height = window.winfo_screenheight() // 1.5




    """
    Method for loading canvas widgets onto main root window

    Parameters:
        -self:      The instance of the GUI class
    Returns:
        -None 
    """
    def load_canvas(window):
        try:
            
            pass

        except Exception as e:
            print(f"Error loading canvas: {e}")



    """
    This method sets the size of the application to the max
    size of the users resoultion

    Parameters:
        -self       The instance of the GUI class
    Returns:
        -None
    """
    def set_geom(self):
        self.window.geometry(f"{self.width}x{self.height}")



class BackgroundImage:
    pass


"""
Class creation of WebcamCapture. Child of GUI, because the webcam 'widget' will go off
elements that reside in the GUI parent class. Elements like the root window resoultion.
"""
class WebcamCapture(GUI):
    
    """
    Instance method of creating a WebcamCapture object. Inherits root window from GUI parent class (tk.Tk) and will create instant
    webcam capture
    """
    def __init__(self, window):

        #Inherit root window from GUI class
        super().__init__(window)
        
        #Set dimensions of webcam feed object that come from the root windows (GUI parent class) 
        self.width = window.winfo_screenwidth() // 2
        self.height = window.winfo_screenheight() // 2

        #Create actual webcam feed with set dimensions ^^^
        vcap = cv2.VideoCapture(0)      #Grab default camera
        vcap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)      
        vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
