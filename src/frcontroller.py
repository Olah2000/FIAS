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
    """
    import face_recognition

    known_encodings = []
    known_names = []

    for filename in os.listdir(faces_folder):
        if filename.lower().endswith(VALID_EXTENSIONS):
            full_path = os.path.join(faces_folder, filename)
            img = face_recognition.load_image_file(full_path)
            encodings = face_recognition.face_encodings(img)
            if len(encodings) == 1:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])

    # Recognition loop
    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=0.1)
        except:
            continue

        if not known_encodings:
            result_queue.put([])
            continue

        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            result_queue.put([])
            continue

        face_encodings = face_recognition.face_encodings(frame, face_locations)
        results = []

        for i, unknown_encoding in enumerate(face_encodings):
            distances = face_recognition.face_distance(known_encodings, unknown_encoding)
            best_match_index = np.argmin(distances)

            if distances[best_match_index] < RECOG_THRESHOLD:
                name = known_names[best_match_index]
                confidence = round(1 - distances[best_match_index], 2)
            else:
                name = "Unknown Student"
                confidence = 0.0

            results.append({
                "name": name,
                "confidence": confidence,
                "location": face_locations[i]
            })

        result_queue.put(results)


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
        self.shared_results = []
        self.faces_folder = faces_folder
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
        self.process = multiprocessing.Process(target = _recognition_worker, args = (self.faces_folder, self.frame_queue, self.result_queue, self.stop_event), daemon = True)
        self.process.start()


    def stop(self):
        self.stop_event.set()
        self.process.join(timeout = 2)



      



    


