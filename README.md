# FIAS
This is a shared repo for Group 1 of Computer Science III

# Setup and Requirements
1. Install and use Visual Studio Code
2. Install Desktop development with C++ and inside 'Installation details' tab check and install MSVC v143 - VS 2022 C++
3. Clone repository
4. Create Python virtual environment and activate it
5. run 'pip install -r requirements.txt' command in terminal


    def update_webcam_feed(self):
        """
        Method for updating the webcam making an actual feed.
        """
        if not self.running:
            return
        frame = self.webcam.get_frame_image()
        if frame is not None:
            photo = PIL.ImageTk.PhotoImage(frame)
            self.webcam_label.config(image = photo)
            self.webcam_label.image = photo
        self.window.after(WEBCAM_FRAME_DELAY_MS, self.update_webcam_feed)




  


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
    