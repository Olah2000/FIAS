"""
Sebastian Olah
Muhammad Usman
Josh Rudnick
 
Application entry point
 
Responsibilities:
    -Construct every major object (GUI, FRC, AttendanceSession, AuditLogger)
    -Wire GUI actions (button commands) to data layer operations
    -Run the Tkinter event loop
 
    GUI.py knows nothing about FRC, AttendanceSession, or AuditLogger.
    main.py is the only file that imports from all layers, making it the
    correct and only place to connect them. keeps each module's
    """
 


import multiprocessing
import tkinter as tk        
from tkinter import messagebox
import numpy as np
from GUI import GUI, WEBCAM_FRAME_DELAY_MS
from GUI import LoginWindow, AddStudentWindow, ManualAttendanceWindow, StudentDashboardWindow
from frcontroller import FRC
from Data import AttendanceSession, Course
from UMAuth import User, Administrator
from audit import AuditLogger
 
 


#Guard section here. Required for multiprocessing on Windows to help frozen executables
 
if __name__ == "__main__":
 
    multiprocessing.freeze_support()    # Essential call for using multiprocess, explicitly documented to be called
                                        
 
    #Root window
    root = tk.Tk(className = " FIAS")   # The space is intentional — it prevents Tkinter from lowercasing "FIAS" in the taskbar/title bar on some platforms.
    root.resizable(False, False)        #No resizing images it sucks.
    
    """
    Where FIAS elements get constructed
    """
 
    FIAS = GUI(root)              # Build the main window (all widgets)
    controller = FRC()                  # Face-recognition controller
    controller.start()                  # Spawn the recognition process
 

    """
    AuditLogger is created before login so that the login attempt itself
    can be logged, creates its log directory on construction
    """

    audit = AuditLogger()
    
    """
    Active course. 
    Represents the class currently being taken attendance for.
    In a fuller implementation the teacher would pick this from
    a dropdown populated from a course database. Buuuuuuuuut not right now
    """

    active_course = Course(name = "Computer Science III", class_id = "CS301", class_name = "CS_III", assigned_teacher = "Mr. Ding", days = ["Mon", "Wed", "Fri"], time = "09:00")
 


    session = AttendanceSession(grace_period_minutes = 5 )
 


    """
     User stored here
     Maps lowercase email to User/Administrator object.
     In a production system this would be loaded from a database or an LDAP
     directory at startup.  The store is passed directly into LoginWindow so
     that the GUI layer never holds a reference to it after authentication.

     !!!!!!!!!!!!!!!!!!HOW TO ADD TEACHERS!!!!!!!!!!!!!!!!!!!:
       user_store["teacher@school.edu"] = User("Name", "teacher@school.edu", "password")
       or for admin rights:
       user_store["admin@school.edu"]   = Administrator("Name", "admin@school.edu", "password")
    """
    user_store = {
        "teacher@school.edu": User(name = "Demo Teacher", email = "teacher@school.edu", pwd   = "password123"),           # swap for a secure credential
        "admin@school.edu": Administrator(name = "Demo Admin", email = "admin@school.edu", pwd   = "adminpass"),
        "tding@dtcc.edu": User(name = "Ken Ding", email = "tding@dtcc.edu", pwd = "123"),
        "student@school.edu": User(name="Demo Student", email="student@school.edu", pwd="student123"),
    }

    # Load saved student accounts from file
    try:
        with open("student_accounts.txt", "r", encoding="utf-8") as file:
            for line in file:
                full_name, email, password = line.strip().split("|")
                user_store[email.lower()] = User(
                    name=full_name,
                    email=email.lower(),
                    pwd=password
                )
    except FileNotFoundError:
        pass
 
    """
    Authenticated teacher name
    Stored in a mutable container (list of one element) so the nested
    on_login_success closure can rebind it.  Python closures can read an
    outer variable but cannot rebind it with `=` unless it is declared
    `nonlocal` using a list avoids the nonlocal keyword for clarity
    """
    current_user = [None]   # current_user[0] will hold the User object
 


    def on_login_success(email):
        """
        Called by LoginWindow immediately before it destroys itself.
        Starts the correct window depending on user type.
        """
        current_user[0] = user_store.get(email.lower())
        audit.log_login(email, success=True)

        teacher_accounts = ["teacher@school.edu", "admin@school.edu", "tding@dtcc.edu"]

        if email.lower() not in teacher_accounts:
            StudentDashboardWindow(root, current_user[0])
        else:
            root.after(10, FIAS.start_webcam)
            root.after(100, update_fs_loop)
 

    """
    Show the login window.  The main window is built and positioned first
    (so LoginWindow can centre itself over it), but it remains inaccessible
    until grab_set() inside LoginWindow routes all events to the dialog.
    """


    login_win = LoginWindow(root, user_store, on_success=on_login_success)
 


    """
    # Main recognition + display loop
    # Track which names have already been marked so we only call mark_present()
    # and audit.log_face_detected() once per student per session, even though
    # get_results() is called ~70 times per second.
    """
    
    _already_marked: set = set()
 


    def update_fs_loop():
        """
        Tkinter's root.after() callback — runs every WEBCAM_FRAME_DELAY_MS ms.
 
        Workflow each tick:
            1. Bail early if webcam is not yet initialised.
            2. Pull the latest PIL frame from WebcamCapture.
            3. Push the numpy version into FRC for recognition.
            4. Pull recognition results back from FRC.
            5. Draw bounding boxes + labels on the PIL frame (display_overlays).
            6. Update the status bar text (display_status).
            7. For each newly-recognised student:
                a. Mark them in AttendanceSession (deduplication lives there).
                b. Audit-log the detection (once per student per session).
            8. Refresh the listbox if the session's name set has grown.
            9. Schedule the next tick.
        """
        if FIAS.webcam is None:
            root.after(WEBCAM_FRAME_DELAY_MS, update_fs_loop)
            return
 
        pil_frame = FIAS.webcam.get_frame_image()
 
        if pil_frame is not None:
            rgb_frame = np.array(pil_frame)         # numpy for face_recognition
            controller.update_frame(rgb_frame)
            results = controller.get_results()
 
            FIAS.display_overlays(results, pil_frame)
            FIAS.display_status(results)
 
            # Mark attendance and audit-log each newly-seen student.
            for r in results:
                name = r["name"]
                if name == "Unknown Student":
                    continue
                session.mark_present(name)

                """
                Read the status back from the #session record that was just written
                """
                if name not in _already_marked:
                    _already_marked.add(name)
                    audit.log_face_detected(name, r["confidence"], session.get_records()[-1]["status"])

            """
            Refresh the listbox only when the session has new records.
            Comparing set sizes is O(1) and avoids a listbox wipe every tick.
            """
            if len(session.get_name_set()) != FIAS.listbox.size():
                FIAS.refresh_listbox(session.get_display_list())
 
        root.after(WEBCAM_FRAME_DELAY_MS, update_fs_loop)
 


 

    """
    Button actions section
    """

    def handle_export():
        """
        Bound to button_export
        Calls AttendanceSession.export_to_csv(), shows the teacher a
        confirmation dialog with the saved filepath, and logs the action.
        """
        filepath = session.export_to_csv(active_course)
        record_count = len(session.get_records())
        user_email = (current_user[0].email if current_user[0] else "unknown")

        audit.log_export(user_email, filepath, record_count)
        messagebox.showinfo("Export Complete", f"Attendance exported to:\n{filepath}\n" f"({record_count} records)")
 


    def handle_add_student():
        """
        Bound to button_captureStudent
        Opens AddStudentWindow only if the webcam is running.  Passing the
        controller in allows AddStudentWindow to stop/restart FRC after saving
        without main.py needing to know the save happened.
        """
        if FIAS.webcam is None:
            messagebox.showwarning("Webcam Not Ready", "Please wait for the webcam to initialise.")
            return
        user_email = (current_user[0].email if current_user[0] else "unknown")
        # AddStudentWindow handles its own audit logging through on-close.
        # pass the audit logger in via a thin wrapper so the window itself
        # does not need to import audit.py.



        def on_student_added(student_name: str, email: str, password: str):
            user_store[email.lower()] = User(name=student_name, email=email.lower(), pwd=password)
            audit.log_student_enrolled(user_email, student_name)



        AddStudentWindow(root, FIAS.webcam, controller, on_student_account_created=on_student_added)
 
    def handle_logout():
        current_user[0] = None

        FIAS.stop_feed()

        if FIAS.webcam is not None:
            FIAS.webcam.cleanup()
            FIAS.webcam = None

        messagebox.showinfo("Logged Out", "You have been logged out.")

        LoginWindow(root, user_store, on_success=on_login_success)

    def handle_manual_attendance():
        """
        Bound to button_manualAttendance.
        Opens ManualAttendanceWindow, which calls session.manual_override()
        on save.  After the window closes the listbox is refreshed so the
        teacher sees the updated status immediately.
        The window is modal (grab_set inside ManualAttendanceWindow), so
        by the time this function returns the teacher has already clicked
        Apply or Cancel.
        """
        user_name = (f"{current_user[0].name}" if current_user[0] else "Unknown Teacher")
 


        def after_override():
            """
            Called after ManualAttendanceWindow destroys itself.
            Refreshes the listbox and audit-logs the change.
            """
            FIAS.refresh_listbox(session.get_display_list())         # Identify the most recently changed record for audit logging.
            records = session.get_records()

            if records:
                last = records[-1]
                audit.log_manual_override(user_name, last["name"], last["status"])
 
        win = ManualAttendanceWindow(root, session)

        # Schedule the post-close refresh to run after the Toplevel destroys.
        root.after(100, after_override)
 


    # Bind the commands now that the handler functions are defined.
    FIAS.button_export.config(command=handle_export)
    FIAS.button_captureStudent.config(command=handle_add_student)
    FIAS.button_manualAttendance.config(command=handle_manual_attendance)
    FIAS.button_logout.config(command=handle_logout)


    def on_app_close():
        """
        Handles exiting the program and ensures all processes / threads shut
        down cleanly before the window is destroyed.
 
        Order matters!!!!
            1. controller.stop() — sends stop_event to the recognition process
               and joins it (timeout=2 s).  Must happen before root.destroy()
               because a daemon process cannot outlive its parent.
            2. FIAS.stop_feed() — sets the running flag so any future
               root.after() callbacks bail immediately.
            3. webcam.cleanup() — releases the cv2 VideoCapture handle so the
               camera is available to other applications after exit.
            4. audit.log_app_close() — writes the session-end marker.
            5. root.destroy() — tears down the Tkinter event loop.
        """
        controller.stop()
        FIAS.stop_feed()

        if FIAS.webcam is not None:
            FIAS.webcam.cleanup()

        audit.log_app_close()
        root.destroy()
 
    root.protocol("WM_DELETE_WINDOW", on_app_close)     #Intercept the window and close button.
    root.mainloop()     # Hand control to the Tkinter event loop.