# Modules (Just for now importing entire module. Will change in later sessions)
import face_recognition
import cv2
import numpy
import tkinter as tk
import PIL.Image
import PIL.ImageTk
from threading import *

"""
get_screen_size is a method that serves to get the resolution of the monitr 
"""
def get_screen_size(root):
    x = root.winfo_screenwidth() // 2
    y = int(root.winfo_screenheight() * 0.5)

    return root.geometry('800x600+' + str(x) + '+' + str(y))



"""
Application window
-Tk() class is used to create

Syntax and Parameters: root = Tk(screenName=None, baseName=None, className='Tk', useTk=1)
-screenName (optional): Specifies the display (mainly used on Unix systems with multiple screens).
-baseName (optional): Sets the base name for the application (default is the script name).
-className (optional): Defines the name of the window class (used for styling and window manager settings).
-useTk (optional): A boolean that tells whether to initialize the Tk subsystem (usually left as default 1).
"""
root = tk.Tk()
root.title("FIAS")
root.eval("tk::PlaceWindow . center")



"""
Frame widget:
-Purpose is to group elements together in a root window
-In this case it will serve as our kind of background for now

Syntax and Parameters: w = Frame(master, options)
-master = The parent widget to which the frame belongs
-options = Set of configuration options written as key-value pairs

    -bg     Sets the background of frame widget
    -bd     Sets the border width around the frame widget (default is 2 pixels)
    -cursor     Changes the cursor when moved over the frame
    -height     Sets the height of frame widget
    -width      Sets the width of the frame widget
    -relief     Defines the border style of the frame widget (FLAT, RAISED, SUNKEN, GROOVE, RIDGE)
    -highlightcolor     
    -highlighbackground
    highlightthickness
"""

#get_screen_size(root)

frame1 = tk.Frame(root, width = 800, height = 600, bg="lightgray")
frame1.grid(row = 0, column = 0)


#Event loop starter
root.mainloop()

#im about to pass out.