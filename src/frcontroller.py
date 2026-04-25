

import face_recognition
import numpy as np
import threading
from GUI import WebcamCapture
import os

RECOG_THRESHOLD = 0.6       #Based on the module, it says that this is the prefered value for letting a face be considered similar

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
        self.shared_frame = None
        self.thread = None
        self.shared_results = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.faces_folder = faces_folder
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
        os.listdir allows us to iterate through all files in the folder by passing in directory to faces folder. Then second part of loop starts.
        Second part checks image file if no face, or many faces. If there's only one, then store the face encoding and name.
        """
        self.validate_folder_path()
    
        for filename in os.listdir(self.faces_folder):     
            if filename.lower().endswith(".png") or filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                full_path = os.path.join(self.faces_folder, filename)
                
                current_img = face_recognition.load_image_file(full_path)       #Load the image file


                current_encoding = face_recognition.face_encodings(current_img)

                if len(current_encoding) == 0:
                    print(f"No face found in image: {filename}, Please check image to ensure a face is present")
                    continue

                if len(current_encoding) > 1:
                    print(f"Multiple faces found in image: {filename}, Please ensure only one face is present in the image")
                    continue
                self.known_encodings.append(current_encoding[0])        #Add the current image's encoding into known encodings
                self.known_names.append(os.path.splitext(filename)[0])      #Add the current image's name into known names



    def process_frame(self, rgb_frame):
        """
        Method that does the face rec processes. Broken into different activites handled my the face_recognition module.

        Methods from face_recognition module:
            -face_locations(frame):     Takes in the Numpy RGB frame (method specifically created in GUI class) and returns coords of face
            -face_encodings(frame, locations):      Takes the frame and locations and returns NumpyArray
            -compare_faces(known_face_encodings, unknown_face_encodings):       Returns a list of True/False values indicating which faces match. Uses a threshold internally 
            -face_distance(known_face_encodings, unknown_face_encodings):       Similar to ^ but returns a float distance other than True/False. Lower = more similar.       
        """
        if not self.known_encodings:
            return []
        


        """
        Locate faces in the frame. Store the face encoding then check
        """
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return []
        


        """
        Encode faces
        """
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        results = []

        for i, unknown_encoding in enumerate(face_encodings):
            distances = face_recognition.face_distance(self.known_encodings, unknown_encoding)
            best_match_index = np.argmin(distances)

            if distances[best_match_index] < RECOG_THRESHOLD:
                name = self.known_names[best_match_index]
                confidence = round(1 - distances[best_match_index], 2)
            else:
                name = "Unknown Student"
                confidence = 0

            results.append({"name": name, "confidence": confidence, "location": face_locations[i]})

  

        self.last_results = results
        return self.last_results
    

    def update_frame(self, rgb_frame):
        with self.lock:
            self.shared_frame = rgb_frame


    
    def get_results(self):
        with self.lock:
            return self.shared_results
        

    def _recognition_loop(self):
        while not self.stop_event.is_set():
            with self.lock:
                frame = self.shared_frame

            if frame is not None:
                results = self.process_frame(frame)
                with self.lock:
                    self.shared_results = results


    def start(self):
        self.thread = threading.Thread(target = self._recognition_loop, daemon = True)
        self.thread.start()


    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout = 2)
