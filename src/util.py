
"""
# Simple method for printing version numbers of imported modules for sanity
# Input: type: module name
# Output: type: string
"""

def ver(module):
    version = getattr(module, "__version__", "Unknown")
    print(f"{module.__name__}: {version}")



"""
Old code for first prototype of GUI object file. Leaving here because I don't 
need it in file anymore, and so I can referance it.


Main window segment... Will polish into with a
proper wrapper but produces a window! (A little past starter code but worth having.)

tkinter = Tk()
cv_bg = cv2.imread("untitled.png")
frame = ttk.Frame(tkinter, padding = 15)
frame.grid()
ttk.Label(frame, text = "Test widget for group project").grid(column = 0, row = 0)
ttk.Button(frame, text = "Exit", command = tkinter.destroy).grid(column = 1, row = 0)
tkinter.mainloop()

attendance_status = "Absent"


Main webcam segment.. Will also wrap up in future sessions
Works! Successfuly makes a frame that's live webcam capture.

capture = webcam.VideoCapture(0)    # 0 is default value webcam device so should NEVER have to change

if not capture.isOpened():
    print("Error opening camera")
    exit()

while True:
    recieved, frame = capture.read()

    if not recieved:
        print("Can't recieve frame")
        break

    #Display
    webcam.imshow("frame", frame)
    if webcam.waitKey(1) == ord("q"):
        break

capture.release()
webcam.destroyAllWindows()





        # ~Window foundation~
        # Load an image now, and create dimensions
        self.windowbase = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

        self.height, self.width, no_channels = self.windowbase.shape

        # Create a canvas, and load background
        self.canvas = tk.Canvas(window, width = self.width, height = self.height)
        self.canvas.pack()

        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.windowbase))
        self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        # Create instance of capture object with hardcoded resolution. This panel is piece of the  whole GUI.
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        


        # ~Webcamera feed foundation~
        def create_capture():
            ret, frame = capture.read()

            if not ret:
                return

            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = PIL.Image.fromarray(opencv_image)
            photo_image = PIL.ImageTk.PhotoImage(image=captured_image)

            self.webwidget.photo_image = photo_image
            self.webwidget.configure(image=photo_image)
            self.webwidget.pack()

            self.webwidget.after(10, create_capture)  # ← reschedule itself!



        #Run window loop
        self.webwidget.after(0, create_capture) 
"""



