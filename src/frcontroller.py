

import face_recognition
import numpy as np
from GUI import WebcamCapture
import os

#import threading

class FRC:
    """
    Instance method for creating FRC (Face Recognition Controller) used to handle all data processing for facial recognition.
    Focus is to save two lists, encodings of faces and names of faces, both stored synchronously for efficiency. Those faces are
    retrieved from iterating through fcs directory in the application folder. 

    Instance variables:

       -self.known_encodings:   List of known face encodings that are stored in fcs folder
       -self.known_names:   List of known face names that correspond to the encodings
       -self.faces_folder:  Path to the folder containing images of known faces
       -self.load_known_faces():    Method to load known face encodings and names from the specified folder
    """
    def __init__(self, faces_folder = "fcs/"):
        self.known_encodings = []
        self.known_names = []
        self.last_results = []
        self.faces_folder = faces_folder
        self.process_this_frame = True
        self.load_known_faces()



    def validate_folder_path(self):
        """
        Validates that the image file actually exists. Lazy imports os to save startup performance
        """
        if not os.path.isdir(self.faces_folder):
            raise FileNotFoundError(f"Faces folder not found: {self.faces_folder}")
        
        





    def load_known_faces(self):
        """
        Method that handles loading known faces from fcs folder, storing their encodings, and storing their name
        os.listdir allows us to iterate through all files in the folder by passing in directory to faces folder. Then second part of loop starts
        """
        self.validate_folder_path()
    
        for filename in os.listdir(self.faces_folder):     
            if filename.lower().endswith(".png") or filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                full_path = os.path.join(self.faces_folder, filename)
                
                current_img = face_recognition.load_image_file(full_path)       #Load the image file


                current_encoding = face_recognition.face_encodings(current_img)

                if len(current_encoding) == 0:
                    raise ValueError(f"No face found in image: {filename}, Please check image to ensure a face is present")

                if len(current_encoding) > 1:
                    raise ValueError(f"Multiple faces found in image: {filename}, Please ensure only one face is present in the image"
                                     )
                self.known_encodings.append(current_encoding[0])        #Add the current image's encoding into known encodings
                self.known_names.append(os.path.splitext(filename)[0])      #Add the current image's name into known names




    """
    def process_frame(self, rgb_frame):
        if not self.process_this_frame:
            return self.last_results
    """

    def process_frame(self, rgb_frame):
        pass

