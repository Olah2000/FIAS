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
