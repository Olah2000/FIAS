import face_recognition
import cv2
import numpy
import tkinter as tk
import PIL.Image
import PIL.ImageTk
from threading import *


def ver(module):
    version = getattr(module, "__version__", "Unknown")
    print(f"{module.__name__}: {version}")

ver(face_recognition)
ver(cv2)
ver(numpy)
ver(PIL.Image)


class GUI:

    def __init__(self, window, window_title, image_path="untitled.png"):
        self.window = window
        self.window.title(window_title)

        # ~Window foundation~
        self.windowbase = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        self.height, self.width, _ = self.windowbase.shape

        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Layer 1 — Background image (painted first, so it sits underneath)
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.windowbase))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # Layer 2 — Webcam feed canvas item (painted second, so it sits on top)
        # Adjust x, y to control where on the background the feed appears
        webcam_x, webcam_y = 20, 20
        self.webcam_item = self.canvas.create_image(
            webcam_x, webcam_y,
            anchor=tk.NW,
            image=None      # Placeholder — filled on first frame
        )

        # ~Webcam capture~
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

        def create_capture():
            ret, frame = capture.read()
            if not ret:
                return

            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = PIL.Image.fromarray(opencv_image)
            photo_image = PIL.ImageTk.PhotoImage(image=captured_image)

            # Update the canvas item's image rather than a Label
            self.canvas.itemconfig(self.webcam_item, image=photo_image)

            # Store reference on the canvas to prevent garbage collection
            # (same reason as before — local variables get destroyed)
            self.canvas.webcam_photo = photo_image

            self.window.after(10, create_capture)

        self.window.after(0, create_capture)
        self.window.mainloop()


GUI(tk.Tk(), "FIAS")