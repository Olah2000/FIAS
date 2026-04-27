"""
Sebastian Olah
Muhammad Usman
Josh Rudnick
"""
 
 
import cv2
import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import PIL.Image
import PIL.ImageTk
import PIL.ImageDraw
import PIL.ImageFont
 
 
"""
Constants here for seating GUI elements nicely
"""
WINDOW_SCALE_FACTOR   = 1.4
WEBCAM_SCALE_FACTOR   = 1.2
WEBCAM_FRAME_DELAY_MS = 14
 






 
class LoginWindow:
    """
    Modal login screen that blocks the main application window until the
    teacher supplies valid credentials.
 
 
    Parameters:

    -parent:        the root tk.Tk window (main application window)

    -user_store:        dict mapping email → User (or Administrator) objects.
                  In a real deployment this would be a database query; for now
                  main.py passes a pre-populated dict.

    -on_success:        callable() invoked when authentication succeeds, before the
                  window is destroyed.  main.py uses this to start the webcam.
    """
 
    def __init__(self, parent, user_store, on_success = None):
        self.parent = parent
        self.user_store = user_store   # { email: User }
        self.on_success = on_success
        self.authenticated = False
 
        #Build Toplevel 
        self.win = tk.Toplevel(parent)
        self.win.title("FIAS — Login Portal")
        self.win.resizable(False, False)
        self.win.configure(bg = "#000615")
 
        #Block all input to the parent window until login succeeds or not
        self.win.grab_set()
 
        #If the teacher closes the dialog without logging in, quit the app.
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
 
        """
        Layout section
        """
        pad = {"padx": 20, "pady": 8}
 
        tk.Label(self.win, text = "FIAS", font = ("JetBrains Mono", 28, "bold"), bg = "#000615", fg = "white").grid(row = 0, column = 0, columnspan = 2, pady =(30, 4))
        tk.Label(self.win, text = "[Facial Identification Attendance System]", font = ("JetBrains Mono", 10), bg = "#000615", fg = "#888888").grid(row = 1, column = 0, columnspan = 2, pady = (0, 20))
 
        tk.Label(self.win, text="Login As", font=("JetBrains Mono", 12), bg="#000615", fg="white").grid(row=2, column=0, sticky="e", **pad)

        self._role_var = tk.StringVar(value="Student")
        role_box = ttk.Combobox(
            self.win,
            textvariable=self._role_var,
            values=["Student", "Teacher/Admin"],
            state="readonly",
            width=26,
            font=("JetBrains Mono", 11)
        )
        role_box.grid(row=2, column=1, **pad)

        # Email field
        tk.Label(self.win, text = "Email", font = ("JetBrains Mono", 12), bg = "#000615", fg = "white").grid(row = 2, column = 0, sticky = "e", **pad)

        self._email_var = tk.StringVar()

        tk.Entry(self.win, textvariable = self._email_var, width = 28, font = ("JetBrains Mono", 12), bg = "#252830", fg = "white", insertbackground = "white", relief = "flat").grid(row = 2, column = 1, **pad)
 
        # Password field
        tk.Label(self.win, text = "Password", font = ("JetBrains Mono", 12), bg = "#000615", fg = "white").grid(row = 3, column = 0, sticky = "e", **pad)
        
        self._pwd_var = tk.StringVar()
        
        tk.Entry(self.win, textvariable = self._pwd_var, show = "•", width = 28, font = ("JetBrains Mono", 12), bg = "#252830",fg = "white", insertbackground = "white", relief = "flat").grid(row = 3, column = 1, **pad)
 
        # Error message label (hidden until a failed attempt).
        self._error_label = tk.Label(self.win, text="", font=("JetBrains Mono", 10), bg="#000615", fg="#ff4444")
        self._error_label.grid(row=4, column=0, columnspan=2)
 
        # Login button — also bound to <Return> for keyboard convenience.
        login_btn = tk.Button(self.win, text="Log In", width=20, height=2, bg="#252830", fg="white", font=("JetBrains Mono", 12), activebackground="#3a3d47", relief="flat", command=self._attempt_login)
        login_btn.grid(row=5, column=0, columnspan=2, pady=(12, 30))
        self.win.bind("<Return>", lambda _e: self._attempt_login())

 
        # Center the dialog over the parent window.
        self.win.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.win.winfo_reqwidth()
        h = self.win.winfo_reqheight()
        self.win.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")
 
    """
    Private helper functions for LoginWindow
    """
 
    def _attempt_login(self):
        """
        Called when the teacher presses Log In or hits Enter.
 
        Looks up the email in user_store.  If found, delegates to
        User.usrlogin() which compares hashed passwords.  This keeps the
        credential comparison logic inside the auth layer (UMAuth.py) where
        it belongs — the GUI just calls it and reacts to the boolean result.
        """
        email = self._email_var.get().strip()
        pwd = self._pwd_var.get()
 
        if not email or not pwd:
            self._show_error("Please enter both email and password.")
            return
 
        user = self.user_store.get(email.lower())
        if user is None or not user.usrlogin(email, pwd):
            self._show_error("Invalid email or password.")
            return
 
        # Success path.
        self.authenticated = True
        if self.on_success:
            self.on_success(email)
        self.win.destroy()

 
    def _show_error(self, message: str):
        """Displays an inline error message below the password field."""
        self._error_label.config(text=message)
 
    def _on_close(self):
        """If the teacher closes the dialog without logging in, exit cleanly."""
        self.parent.destroy()
 



class StudentDashboardWindow:
    """
    Student dashboard window.
    Allows students to view attendance records and submit attendance correction requests.
    """

    def __init__(self, parent, student_user):
        self.parent = parent
        self.student_user = student_user

        self.win = tk.Toplevel(parent)
        self.win.title("FIAS — Student Dashboard")
        self.win.resizable(False, False)
        self.win.configure(bg="#000615")
        self.win.grab_set()

        tk.Label(
            self.win,
            text="Student Dashboard",
            font=("JetBrains Mono", 22, "bold"),
            bg="#000615",
            fg="white"
        ).grid(row=0, column=0, columnspan=2, pady=(25, 10))

        tk.Label(
            self.win,
            text=f"Welcome, {student_user.name}",
            font=("JetBrains Mono", 13),
            bg="#000615",
            fg="#cccccc"
        ).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        tk.Label(
            self.win,
            text="Attendance Records",
            font=("JetBrains Mono", 14, "bold"),
            bg="#000615",
            fg="white"
        ).grid(row=2, column=0, columnspan=2, pady=(5, 5))

        self.records_box = tk.Listbox(
            self.win,
            width=50,
            height=8,
            bg="#252830",
            fg="white",
            font=("JetBrains Mono", 11),
            borderwidth=0,
            highlightthickness=0
        )
        self.records_box.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        # Demo attendance records for prototype
        demo_records = [
            "Computer Science III - Present",
            "Software Engineering - Late",
            "Database Systems - Absent"
        ]

        for record in demo_records:
            self.records_box.insert(tk.END, record)

        tk.Label(
            self.win,
            text="Request Attendance Correction",
            font=("JetBrains Mono", 14, "bold"),
            bg="#000615",
            fg="white"
        ).grid(row=4, column=0, columnspan=2, pady=(15, 5))

        tk.Label(
            self.win,
            text="Date",
            font=("JetBrains Mono", 12),
            bg="#000615",
            fg="white"
        ).grid(row=5, column=0, sticky="e", padx=15, pady=6)

        self.date_var = tk.StringVar()
        tk.Entry(
            self.win,
            textvariable=self.date_var,
            width=28,
            font=("JetBrains Mono", 12),
            bg="#252830",
            fg="white",
            insertbackground="white",
            relief="flat"
        ).grid(row=5, column=1, padx=15, pady=6)

        tk.Label(
            self.win,
            text="Reason",
            font=("JetBrains Mono", 12),
            bg="#000615",
            fg="white"
        ).grid(row=6, column=0, sticky="ne", padx=15, pady=6)

        self.reason_box = tk.Text(
            self.win,
            width=28,
            height=4,
            font=("JetBrains Mono", 12),
            bg="#252830",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.reason_box.grid(row=6, column=1, padx=15, pady=6)

        tk.Button(
            self.win,
            text="Submit Request",
            width=20,
            height=2,
            bg="#252830",
            fg="white",
            font=("JetBrains Mono", 12),
            relief="flat",
            activebackground="#3a3d47",
            command=self.submit_request
        ).grid(row=7, column=0, columnspan=2, pady=(15, 25))

        self.win.update_idletasks()
        w = self.win.winfo_reqwidth()
        h = self.win.winfo_reqheight()
        self.win.geometry(f"{w}x{h}")

    def submit_request(self):
        date = self.date_var.get().strip()
        reason = self.reason_box.get("1.0", tk.END).strip()

        if not date or not reason:
            messagebox.showwarning("Missing Information", "Please enter both date and reason.")
            return

        messagebox.showinfo(
            "Request Submitted",
            "Your attendance correction request has been submitted."
        )

        self.date_var.set("")
        self.reason_box.delete("1.0", tk.END)








 
class AddStudentWindow:
    """
    Modal window that captures the current webcam frame, shows it as a
    preview, accepts a first/last name, and saves the image to fcs/ so that
    FRC will recognise the student on the next session start.
 
    Parameters:

        -parent:        root tk.Tk window
        -webcam:        live WebcamCapture instance (to grab the preview frame)
        -controller:        FRC instance (stopped before save, restarted after)
        -faces_folder:      path to fcs/ directory — must match FRC's faces_folder
    """
 
    def __init__(self, parent, webcam, controller, faces_folder: str = "fcs/", on_student_account_created=None):
        self.parent = parent
        self.webcam = webcam
        self.controller = controller
        self.on_student_account_created = on_student_account_created
        self.faces_folder = faces_folder
        self._captured_image = None   # PIL Image grabbed at window open time
 

        #Create Toplevel
        self.win = tk.Toplevel(parent)
        self.win.title("FIAS — Add Student")
        self.win.resizable(False, False)
        self.win.configure(bg = "#000615")
        self.win.grab_set()
 
        """
        
        grab one frame immediately for the preview
        We take the snapshot the instant the window opens so the teacher
        can position the student before pressing Add.  A "Retake" button
        lets them refresh the snapshot if the first frame was bad.
        """
        self._grab_frame()
 
        preview_w, preview_h = 320, 240
        self._canvas = tk.Canvas(self.win, width=preview_w, height=preview_h, bg="#252830", highlightthickness=0)
        self._canvas.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 8))
        self._render_preview()
 
        tk.Button(self.win, text="Retake Photo", width=20, bg="#252830", fg="white", font=("JetBrains Mono", 11), relief="flat", activebackground="#3a3d47", command=self._retake).grid(row=1, column=0, columnspan=2, pady=(0, 12))


        """
        Name entry section
        """
        pad = {"padx": 20, "pady": 6}
 
        tk.Label(self.win, text="First Name", font=("JetBrains Mono", 12), bg="#000615", fg="white").grid(row=2, column=0, sticky="e", **pad)
        self._fname_var = tk.StringVar()
        tk.Entry(self.win, textvariable=self._fname_var, width=22, font=("JetBrains Mono", 12), bg="#252830", fg="white", insertbackground="white", relief="flat").grid(row=2, column=1, **pad)
 
        tk.Label(self.win, text="Last Name", font=("JetBrains Mono", 12), bg="#000615", fg="white").grid(row=3, column=0, sticky="e", **pad)
        
        self._lname_var = tk.StringVar()
        tk.Entry(self.win, textvariable = self._lname_var, width = 22, font = ("JetBrains Mono", 12), bg = "#252830", fg = "white", insertbackground = "white", relief = "flat").grid(row = 3, column = 1, **pad)

        tk.Label(
            self.win,
            text="Student Email",
            font=("JetBrains Mono", 12),
            bg="#000615",
            fg="white"
        ).grid(row=4, column=0, sticky="e", **pad)

        self._email_var = tk.StringVar()

        tk.Entry(
            self.win,
            textvariable=self._email_var,
            width=22,
            font=("JetBrains Mono", 12),
            bg="#252830",
            fg="white",
            insertbackground="white",
            relief="flat"
        ).grid(row=4, column=1, **pad)


        tk.Label(
            self.win,
            text="Password",
            font=("JetBrains Mono", 12),
            bg="#000615",
            fg="white"
        ).grid(row=5, column=0, sticky="e", **pad)

        self._password_var = tk.StringVar()

        tk.Entry(
            self.win,
            textvariable=self._password_var,
            show="*",
            width=22,
            font=("JetBrains Mono", 12),
            bg="#252830",
            fg="white",
            insertbackground="white",
            relief="flat"
        ).grid(row=5, column=1, **pad)
 
        """
        Error display section
        """
        self._error_label = tk.Label(self.win, text = "", font = ("JetBrains Mono", 10), bg = "#000615", fg = "#ff4444")
        self._error_label.grid(row = 6, column = 0, columnspan =2 )


 
        """
        #Action buttons secotion
        """
        btn_frame = tk.Frame(self.win, bg = "#000615")
        btn_frame.grid(row = 7, column = 0, columnspan = 2, pady = (8, 20))
 
        tk.Button(btn_frame, text = "Save Student", width = 16, height = 2, bg = "#252830", fg = "white", font = ("JetBrains Mono", 11), relief = "flat", activebackground = "#3a3d47",command = self._save).pack(side = "left", padx = 8)
        tk.Button(btn_frame, text = "Cancel", width = 12, height = 2, bg = "#252830", fg = "#888888", font = ("JetBrains Mono", 11), relief = "flat", activebackground = "#3a3d47", command = self.win.destroy).pack(side = "left", padx = 8)
 
        # Center over parent
        self.win.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w,  h  = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        self.win.geometry(f"{w}x{h}+{px + (pw-w)//2}+{py + (ph-h)//2}")


 
    """
    'Private method functions primarily used for multiprocesses for extra window support
    """
 
    def _grab_frame(self):
        """
        Captures one RGB frame from the webcam and stores it as a PIL Image.
        If the webcam returns nothing (camera not ready), _captured_image
        stays None and the canvas will show a placeholder message.
        """
        self._captured_image = self.webcam.get_frame_image()


 
    def _render_preview(self):
        """
        Method for drawing the captured PIL Image onto the preview canvas.
        Scales it to fit within the 320×240 canvas while preserving aspect
        ratio. If no image is available, displays an error hint instead.
        """
        self._canvas.delete("all")

        if self._captured_image is None:
            self._canvas.create_text(160, 120, text = "Camera not ready.\nPress Retake.", fill = "#888888", font = ("JetBrains Mono", 12), justify = "center")
            return
 
        preview = self._captured_image.copy()
        preview.thumbnail((320, 240), PIL.Image.LANCZOS)
        self._tk_preview = PIL.ImageTk.PhotoImage(preview)

        # Center the thumbnail on the canvas regardless of its actual size.
        x = (320 - preview.width)  // 2
        y = (240 - preview.height) // 2
        self._canvas.create_image(x, y, anchor = "nw", image = self._tk_preview)
 
    def _retake(self):
        """Grabs a fresh frame and re-renders the preview."""
        self._grab_frame()
        self._render_preview()
 
    def _save(self):
        """
        Validates the name fields, saves the image to fcs/, then restarts
        FRC so it loads the new face encoding immediately.
 
        Validation rules:
            - Both first and last name must be non-empty.
            - A captured image must exist (retake if camera wasn't ready).
            - The destination filename must not already exist (prevents
              accidentally overwriting an existing student's photo).
 
        After a successful save:
            controller.stop():      join the recognition process.
            controller.start():     spawn a fresh process that re-scans fcs/.
        """
        fname = self._fname_var.get().strip()
        lname = self._lname_var.get().strip()
        email = self._email_var.get().strip().lower()
        password = self._password_var.get().strip()

        if not fname or not lname or not email or not password:
            self._error_label.config(text="Name, email, and password are required.")
            return
 
        if self._captured_image is None:
            self._error_label.config(text="No image captured. Press Retake.")
            return
 
        # Build the filename exactly as FRC expects: "First Last.png"
        full_name = f"{fname} {lname}"
        dest_path = os.path.join(self.faces_folder, f"{full_name}.png")
 
        if os.path.exists(dest_path):
            self._error_label.config(
                text=f"Student '{full_name}' already exists in fcs/."
            )
            return
 
        os.makedirs(self.faces_folder, exist_ok=True)
 
        # Convert from RGB (PIL default from webcam) to RGB PNG — no
        # channel swap needed since face_recognition also expects RGB.
        self._captured_image.save(dest_path, format="PNG")

        with open("student_accounts.txt", "a", encoding="utf-8") as file:
            file.write(f"{full_name}|{email}|{password}\n")

        if self.on_student_account_created:
            self.on_student_account_created(full_name, email, password)
 
        # Restart FRC so the new encoding is loaded into the worker process.
        self.controller.stop()
        self.controller.start()
 
        messagebox.showinfo("Student Added", f"{full_name} has been enrolled successfully.")
        self.win.destroy()
 
 


















 
class ManualAttendanceWindow:
    """
    Modal dialog that lets a teacher manually set or override the attendance
    status of any student, whether or not they were detected by the camera.
    The Listbox widget does not support in-place editing natively.  Replacing it
    with a Treeview (which does) would require significant changes to existing
    GUI code.  A lightweight modal avoids touching any existing code and follows
    the project's pattern of using Toplevels for teacher actions.
 
    Parameters:

        -parent:        root tk.Tk window
        -session:       live AttendanceSession — manual_override() is called on save
    """
 
    STATUSES = ["Present", "Late", "Absent", "Excused"]
 
    def __init__(self, parent: tk.Tk, session) -> None:
        self.parent  = parent
        self.session = session
 
        self.win = tk.Toplevel(parent)
        self.win.title("FIAS — Manual Attendance")
        self.win.resizable(False, False)
        self.win.configure(bg="#000615")
        self.win.grab_set()
 
        pad = {"padx": 20, "pady": 8}
 
        tk.Label(self.win, text="Manual Attendance Override",
                 font=("JetBrains Mono", 14, "bold"),
                 bg="#000615", fg="white").grid(row=0, column=0,
                                                columnspan=2, pady=(20, 8))
 
        # Student name entry — must match the fcs/ filename stem exactly.
        tk.Label(self.win, text="Full Name", font=("JetBrains Mono", 12),
                 bg="#000615", fg="white").grid(row=1, column=0,
                                                sticky="e", **pad)
        self._name_var = tk.StringVar()
        tk.Entry(self.win, textvariable=self._name_var, width=26,
                 font=("JetBrains Mono", 12), bg="#252830",
                 fg="white", insertbackground="white",
                 relief="flat").grid(row=1, column=1, **pad)
 
        # Status dropdown
        tk.Label(self.win, text="Status", font=("JetBrains Mono", 12),
                 bg="#000615", fg="white").grid(row=2, column=0,
                                                sticky="e", **pad)
        self._status_var = tk.StringVar(value="Present")
        status_menu = ttk.Combobox(self.win, textvariable=self._status_var,
                                   values=self.STATUSES, state="readonly",
                                   width=24, font=("JetBrains Mono", 11))
        status_menu.grid(row=2, column=1, **pad)
 
        # Error label
        self._error_label = tk.Label(self.win, text="",
                                     font=("JetBrains Mono", 10),
                                     bg="#000615", fg="#ff4444")
        self._error_label.grid(row=3, column=0, columnspan=2)
 
        # Action buttons
        btn_frame = tk.Frame(self.win, bg="#000615")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 20))
 
        tk.Button(btn_frame, text="Apply", width=14, height=2,
                  bg="#252830", fg="white", font=("JetBrains Mono", 11),
                  relief="flat", activebackground="#3a3d47",
                  command=self._apply).pack(side="left", padx=8)
 
        tk.Button(btn_frame, text="Cancel", width=10, height=2,
                  bg="#252830", fg="#888888", font=("JetBrains Mono", 11),
                  relief="flat", activebackground="#3a3d47",
                  command=self.win.destroy).pack(side="left", padx=8)
 
        # Centre over parent
        self.win.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w,  h  = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        self.win.geometry(f"{w}x{h}+{px + (pw-w)//2}+{py + (ph-h)//2}")
 
    def _apply(self) -> None:
        """Validates inputs and calls session.manual_override()."""
        name   = self._name_var.get().strip()
        status = self._status_var.get()
 
        if not name:
            self._error_label.config(text="Please enter the student's full name.")
            return
 
        self.session.manual_override(name, status)
        messagebox.showinfo("Attendance Updated",
                            f"{name} marked as {status}.")
        self.win.destroy()
 




















 
class GUI:
    """
    Instance method of GUI class.
 
    Parameters:
        -window:    The main window object
        -image_path:    The path to the background image file to be displayed.
 
    Instance variables:
        -self.window:   An instance of a tk.Tk() (root in main)
        -self.image_path:   The path to the background image file to be displayed
        -self.bimg:     Background image itself
        -self.menu:     Menu widget to create menu bar
        -self.background_label:     Tkinter label widget with background to identify it
        -self.width:   The width of the application window
        -self.height:   The height of the application window
        -self.running:  Flag for neat shutdown operations
        -self.webcam:   Composed instance of WebcamCapture class inside GUI class.
    """
    def __init__(self, window, image_path = "wf/FIASLAYOUT.png"):
        self.window = window
        self.image_path = image_path
        self.canvas = None
        self.bgimg = None
        self.button_export = None
        self.button_captureStudent = None
        self.button_viewClasses = None
        self.button_manualAttendance = None
        self.listbox = None
        self.background_label = None
        self.menu = None
        self.create_menu()
        self.width = int(window.winfo_screenwidth() / WINDOW_SCALE_FACTOR)
        self.height = int(window.winfo_screenheight() / WINDOW_SCALE_FACTOR)
        self.running = True
        self.webcam = None
 
 
 
        """
        ALL STATIC COMPONENTS TO GUI INITIALIZED HERE WITHOUT METHODS.
 
 
        Uploading background image section. Composes BackgrounImage in GUI with these lines.
        bgimg is initialized as a BackgroundImage object w all properties, tkinter label is created, and is placed
        """
        if image_path:
            self.bgimg = BackgroundImage(image_path, self.width, self.height)
            self.background_label = tk.Label(window, image = self.bgimg.get_photo_image())
            self.background_label.place(x = 0, y = 0, relheight = 1, relwidth = 1)
 
 
        
        """
        Setting webcam capture in root window. 
            -self.webcam_label:     Tkinter label for placing the webcam feed inside the root window
            -self.webcam_label.place:   Method for putting the label at a specific position. (A geometry manager, simple so using it here) 
            -self.update_webcam_feed():     Calling the method to update the webcam feed and feed frames
        """
        self.webcam_label = tk.Label(window)
        self.webcam_label.place(relx = 0.5, rely = 0.5, anchor = "center")
 
        self.status_label = tk.Label(window, text = "No face detected", font = ("JetBrains Mono", 20), bg = "#000615", fg = "white")
        self.status_label.place(relx = 0.5, rely = 0.9, anchor = "center")
 
 
 
        """
        List box initialization for student's marked present by face scan.
 
        Search Entry widget is placed above the listbox.
        It filters the listbox contents live as the teacher types.
        The SearchBar is composed here exactly as BackgroundImage and
        WebcamCapture are composed — GUI has-a SearchBar.
        """
        self.search_bar = SearchBar(window, self._on_search)
        self.search_bar.place(relx=0.1154, rely=0.28, anchor="center")
 
        self.listbox = tk.Listbox(window, bg = "#252830", fg = "white", font = ("JetBrains Mono", 13), borderwidth = 0, highlightthickness = 0)
        self.listbox.place(relx = 0.1154, rely = 0.4, anchor = "center")
 
        # Internal cache of the full (unfiltered) display list so the search
        # bar can re-populate the listbox without needing access to the session.
        self._full_display_list: list[str] = []
 
 
        
        """
        Button widget initialization for tools that teach can use.
        """
        self.button_export = tk.Button(window, text = "Export", width = 15, height = 2, bg = "#252830", fg = "white", font = ("JetBrains Mono", 13))
        self.button_captureStudent = tk.Button(window, text = "Add Student", width = 15, height = 2, bg = "#252830", fg = "white", font = ("JetBrains Mono", 13))
        self.button_viewClasses = tk.Button(window, text = "View Classes", width = 15, height = 2, bg = "#252830", fg = "white", font = ("JetBrains Mono", 13))
        self.button_manualAttendance = tk.Button(window, text="Manual Mark", width = 15, height = 2, bg = "#252830", fg = "white", font = ("JetBrains Mono", 13))
        self.button_logout = tk.Button(window, text="Logout", width=15, height=2, bg="#252830", fg="white", font=("JetBrains Mono", 13))


        self.button_export.place(relx = 0.8845, rely = 0.3, anchor = "center")
        self.button_captureStudent.place(relx = 0.8845, rely = 0.4, anchor = "center")
        self.button_viewClasses.place(relx = 0.8845, rely = 0.5, anchor = "center")
        self.button_manualAttendance.place(relx=0.8845, rely=0.6, anchor="center")
        self.button_logout.place(relx=0.8845, rely=0.7, anchor="center")  # NEW
 
 
 
 
        self.set_window_size()  #Organizes everything after initialized in
 
#~~~~~~~~~~~~~~~~~~~END GUI INIT~~~~~~~~~~~~~~~~~~~~~#
 
 
 
    def set_window_size(self):
        """
        This method sets the size of the application to the 1/6th of the users resolution
        """
        try:
            self.window.geometry(f"{self.width}x{self.height}")
        except Exception as e:
            raise RuntimeError(f"Could not find usable resolution. Error: {e}")
        
      
      
    def create_menu(self):
        """
        Method for creating a menu bar for added user experience functionality
        Has to be intialized upon GUI creation because it is static, and because of how stupid tkinter is.
        """
        menu = tk.Menu(self.window, activebackground = "#252627")
        filemenu = tk.Menu(menu, tearoff = 0, activebackground = "#1f2430")
        menu.add_cascade(label = "File", menu = filemenu)
        filemenu.add_command(label = "New", command = None)
        filemenu.add_command(label = "Open...", command = None)
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = self.window.quit)
        self.window.config(menu = menu)
        self.menu = menu
            
 
 
  
    def start_webcam(self):
        self.webcam = WebcamCapture()
 
 
 
    def display_overlays(self, results, frame):  # frame passed in, not re-read
 
        if frame is None:
            return
        
        draw = PIL.ImageDraw.Draw(frame)
 
        for result in results:
            top, right, bottom, left = result["location"]
            name = result["name"]
            confidence = result["confidence"]
 
            if name == "Unknown Student":
                color = "red"
            else:
                color = "green"
 
            draw.rectangle([left, top, right, bottom], outline = color, width = 2)
            draw.text((left, top), f"{name}: {confidence:.2f}", fill = "black")
 
        photo = PIL.ImageTk.PhotoImage(frame)
        self.webcam_label.config(image = photo)
        self.webcam_label.image = photo
 
 
 
    def display_status(self, results):
        """
        Method that actually handles the status label based on recognition results
        """
        if not results:
            message = "No face detected"
        elif any(r["name"] == "Unknown Student" for r in results):
            message = "Unknown student detected"
        else:
            names = [r["name"] for r in results]
            message = f"Recognized: {', '.join(names)}"
 
        self.status_label.config(text = message)
 

 
    def refresh_listbox(self, display_list):
        """
        Replaces the listbox contents with `display_list` and updates
        the internal cache used by the search bar filter.
 
        Called from main.py's update_fs_loop() every tick that produces new
        attendance records. 
        """
        self._full_display_list = display_list
        self._populate_listbox(display_list)
 
 
    def _populate_listbox(self, entries):
        """Clears the Listbox and inserts the given entries."""
        self.listbox.delete(0, tk.END)

        for entry in entries:
            self.listbox.insert(tk.END, entry)
 
 
    def _on_search(self, query):
        """
        Callback wired into SearchBar. Filters the cached display list
        and repopulates the listbox with matching rows.
        Called every time the teacher types in the search field.
        """
        if not query:
            self._populate_listbox(self._full_display_list)
            return
        q       = query.lower()
        filtered = [e for e in self._full_display_list if q in e.lower()]
        self._populate_listbox(filtered)
 
 
    def stop_feed(self):
        """
        Flag raiser to stop feed instnatly when user closes application
        """
        self.running = False
 
 




















 
class SearchBar:
    """
    Entry widget composed into GUI above the Listbox.
 
        # Trace every write to the StringVar so filtering is instant.
    
    Parameters:
        parent: tk widget that owns this search bar
        on_change: callable(str) called with the current search text every time the content of the Entry changes.
    """
 
    def __init__(self, parent, on_change):
        self._on_change = on_change
        self._var = tk.StringVar()
        self._var.trace_add("write", self._handle_change)
 
        self._frame = tk.Frame(parent, bg="#000615")
 
        tk.Label(self._frame, text = "🔍", font = ("JetBrains Mono", 11), bg = "#000615", fg = "#888888").pack(side = "left", padx = (0, 4))
 
        self._entry = tk.Entry(self._frame, textvariable = self._var, width = 16, font = ("JetBrains Mono", 11), bg = "#252830", fg = "white", insertbackground = "white", relief = "flat")
        self._entry.pack(side="left")
 
    def place(self, **kwargs):
        """Delegates geometry management to the internal frame."""
        self._frame.place(**kwargs)
 
    def _handle_change(self, *_args) -> None:
        """StringVar trace callback — strips and forwards the current value."""
        self._on_change(self._var.get().strip())
 
 



















class BackgroundImage:
 
    """
    Instance method of creating BackgroundImage objects. This object is COMPOSED (Not inherited.
    two different things. Better. Establishes more of a 'has-a' relationship whereas inheritance creates a 'is-a' relationship
    Better for this kind of architecture when working with a GUI.
    im rambling. Just initialize the fucking object)
    
    Parameters:
        -self.image_path:    The path to the background image
        -self.width:     The width of the background image
        -self.height:    The height of the background image
        -self.bgimg:    
    """
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.bgimg = None
 
 
 
        #Error handling in case image loading goes awry
        try:
            self.validate_image_path()
            self.load_image()
        except Exception as e:
            print(f"Failed to initialize background image. Error: {e}")
 
 
 
    def validate_image_path(self):
        """
        Valides that the image file actually exists. Lazy imports os to save startup performance
        """
        import os
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image file not found: {self.image_path}")
 
 
 
    def load_image(self):
        """
        Method for opening image with Pillow, resizing, then making it PILTk and initalization variable.
        'image' is a local variable to hold the PIL Image object, and then becomes 'self.bgimg' and turned into tkinter widget
        """
        image = PIL.Image.open(self.image_path)
        image = image.resize((int(self.width), int(self.height)))
        self.bgimg = PIL.ImageTk.PhotoImage(image)
 
 
 
    def get_photo_image(self):
        """
        Helper function to retrieve the background image of the GUI
        """
        return self.bgimg
 
 














 
class WebcamCapture:
    """
    Instance method of creating a WebcamCapture object. COMPOSED in root window from GUI class (tk.Tk) and will create instant
    webcam capture
 
    Initialization variables:
        -self.width:    width of webcam feed object
         -self.height:   height of webcam feed object
         -self.vcap:     Instance of webcam feed object
    """
    def __init__(self):
        self.width = 640
        self.height = 480
        self.frame_queue = queue.Queue(maxsize = 1)
 
        self.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)      #Grab default camera
 
 
        #Create actual webcam feed with set dimensions ^^^
        self.vcap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.width / WEBCAM_SCALE_FACTOR))      
        self.vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.height / WEBCAM_SCALE_FACTOR))
 
        self.thread = threading.Thread(target = self._capture_loop, daemon = True)
        self.thread.start()
 
 
    def _capture_loop(self):
        """Runs on its own thread. Never blocks the GUI."""
        while True:
            ret, frame = self.vcap.read()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
 
            # Drain the queue first so we always have the freshest frame
            if not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            self.frame_queue.put_nowait(rgb)
 
 
 
 
    def get_frame_rgb(self):
        """Non-blocking. Returns None if no frame is ready yet."""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
 
 
 
    def get_frame_image(self):
        """
        Method for converting the captured frame to a PIL Image. This is used for the GUI only and can't be used for any
        kind of data processing
        """
        rgbframe = self.get_frame_rgb()
        if rgbframe is None:
            return None
        return PIL.Image.fromarray(rgbframe)
    
 
 
    def cleanup(self):
        """
        Cleanup method that should be called whenever the webcam capture is no longer needed
        """
        if self.vcap.isOpened():
            self.vcap.release()