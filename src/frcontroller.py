

import numpy as np
import multiprocessing
import os
    

    
RECOG_THRESHOLD = 0.6
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg")



def _recognition_worker(faces_folder, frame_queue, result_queue, stop_event):
    """
    MAIN METHOD FOR PROCESSING FACE DATA AND COMPARING. This is declared module wide because mutliprocess needs to access this inside
    the class. Btw the leading _ apparenetly signals the Python interpreter to not import this in another class when victim of 'from module import *'
    Anyway, this worker:
        -Establishes a picture's encodings, and name to the face
        -Verify's directory fcs that stores the raw VALID_EXTENSIONS' pictures.
        - Iterates over each file, stores data from them
        -Checks if there IS a face in the encoding (comapring to length 1) then appends the encoding and name of the person (File name MUST be first and last name of person) to list

    Parameters:
        -faces_folder:      Relative path (of project folder) to directory of face images
        -frame_queue:       Queued frame that gets piped from multiprocessed method out to the FRC class back into the main process to be used
        -result_queue:      Queued result that gets piped from multiprocessed method out to the FRC class back into the main process to be used
        -stop_event:        Initialized as True by default. So when loop starts, it is check if it's False.
    """
    import face_recognition

    known_encodings = []
    known_names = []

    """
    Verification
    """
    for filename in os.listdir(faces_folder):
        if filename.lower().endswith(VALID_EXTENSIONS):
            full_path = os.path.join(faces_folder, filename)
            img = face_recognition.load_image_file(full_path)
            encodings = face_recognition.face_encodings(img)
            if len(encodings) == 1:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])

    """
    Start recognition loop
    """
    while not stop_event.is_set():      #Flag signal to continue or stop face rec process. If on, the current frame is the one frame queued
        try:
            frame = frame_queue.get(timeout = 0.1)
        except:
            continue

        """
        ~Important~
        This line first checks is the list is empty. This is encapsulated in the while loop, scanning if any list is empty.
        List because each face_locations returns 2d array.
        """
        if not known_encodings:
            result_queue.put([])
            continue


        face_locations = face_recognition.face_locations(frame)     #Get face_locations from frame

        if not face_locations:      #If face_locations is empty, put empty list in queue
            result_queue.put([])       
            continue

        face_encodings = face_recognition.face_encodings(frame, face_locations)     #face_encoding returns a list of 128-dimensional face_encodings 
        results = []


        
        for i, unknown_encoding in enumerate(face_encodings):
            distances = face_recognition.face_distance(known_encodings, unknown_encoding)       #Compare faces against learned faces in folder to face present on camera. Returns a list of tuples of face locations
            best_match_index = np.argmin(distances)     #Find the minimum distance. Right now, the lower confidence is better before readable adjustements bellow



            if distances[best_match_index] < RECOG_THRESHOLD:       
                name = known_names[best_match_index]
                confidence = round(1 - distances[best_match_index], 2)
            else:
                name = "Unknown Student"
                confidence = 0.0

            results.append({        #If confident scan, add student information to list
                "name": name,
                "confidence": confidence,
                "location": face_locations[i]
            })

        result_queue.put(results)       #Put result data in queue to ship to main process (Rest of application)

































class FRC:
    """
    Instance method for creating FRC (Face Recognition Controller) used to handle all data processing for facial recognition.
    Focus is to save two lists, encodings of faces and names of faces, both stored synchronously for efficiency. Those faces are
    retrieved from iterating through fcs directory in the application folder. 

    Instance variables:

       -self.known_encodings:       List of known face encodings that are stored in fcs folder
       -self.known_names:       List of known face names that correspond to the encodings
       -self.faces_folder:      String of the path to the folder containing images of known faces
       -self.frame_queue:       FRC's frame queue from _recognition_worker method. (Below are same) Used to take in data from another process
       -self.result_queue:
       -self.stop_event:
       -self.process:
       -self.last_results:
    """
    def __init__(self, faces_folder = "fcs/"):
        self.known_encodings = []
        self.known_names = []
        self.shared_results = []
        self.faces_folder = faces_folder
        self.validate_folder_path()
        self.frame_queue = multiprocessing.Queue(maxsize = 1)
        self.result_queue = multiprocessing.Queue(maxsize = 1)
        self.stop_event = multiprocessing.Event()
        self.process = None
        self.last_results = []
  


    def validate_folder_path(self):
        """
        Validates that the image file actually exists. Lazy imports os to save startup performance
        """
        if not os.path.isdir(self.faces_folder):
            raise FileNotFoundError(f"Faces folder not found: {self.faces_folder}")



    def update_frame(self, rgb_frame):
        """
        Method that gets the data from the frame queue if its not empty. And if it's not then grab the rgb_frame from it (face_rec takes Numpy which is cv2)
        """
        if not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                pass
        try:
                self.frame_queue.put_nowait(rgb_frame)
        except:
            pass



    def get_results(self):
        try:
            self.last_results = self.result_queue.get_nowait()
        except:
            pass
        return self.last_results
    

    
    def start(self):
        """
        One of the key methods for starting the multiprocess. Targets the _recognition method, and plugs in FRC instance variables to be put into GUI
        """
        self.process = multiprocessing.Process(target = _recognition_worker, args = (self.faces_folder, self.frame_queue, self.result_queue, self.stop_event), daemon = True)
        self.process.start()


   
    def stop(self):
        """
        Flag setter function to properly stop multiprocess.
        """
        self.stop_event.set()
        self.process.join(timeout = 2)



      



    


