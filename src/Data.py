"""
Sebastian Olah
Muhammad Usman
Josh Rudnick
 
UML Diagram Assignment
CSIII
Mr. Ding
"""








import face_recognition
import numpy
import csv
import os
import time
from datetime import datetime
 

 
class Course:
    """
    Represents a scheduled class section.
 
    Parameters:

        -name:      display name of the course  (e.g. "Computer Science III")
        -class_id:      unique identifier           (e.g. "CS301")
        -class_name:        hort label used in filenames
        -assigned_teacher:      teacher's full name string
        -days:      list of day abbreviations   (e.g. ["Mon", "Wed", "Fri"])
        -time:      start time string           (e.g. "09:00")
    """
 
    def __init__(self, name: str, class_id, class_name: str, assigned_teacher: str, days, time):
        self.name = name
        self.class_id = class_id
        self.class_name = class_name
        self.assigned_teacher = assigned_teacher
        self.days = days
        self.time = time
 












 
class Student(Course):
    """
    Represents an enrolled student.
 
    Inherits Course so that a Student object carries the class context it
    belongs to alongside its personal data — matching the original UML intent.
 
    Parameters:

        -fname:      first name
        -lname:      last name
        -stu_email:      institutional e-mail address
        -face_scan_data:     raw 128-d face encoding (numpy array) or None
        -last_picture:       file path to the student's reference photo or None
    """
    def __init__(self, fname, lname, stu_email, face_scan_data, last_picture):
        self.first_name = fname
        self.last_name = lname
        self.stu_email = stu_email
        self.face_scan_data = face_scan_data
        self.last_picture = last_picture


        """
        Initialise the Course portion with empty values until the student
        is assigned to a specific class section.
        """
        
        Course.__init__(self, name = None, class_id = None, class_name = None, assigned_teacher = None, days = None, time = None)
 

        self.attendance_days: list[dict] = []       # Attendance history across all sessions — list of dicts keyed by date.
 
 





























class Teacher:
    """
    Represents an authenticated teacher.
    """
    def __init__(self, tfname, tlname, teacher_id, tTOTPsecret):
        self.tfirst_name = tfname
        self.tlast_name = tlname
        self.teacher_id = teacher_id
        self._totp_secret = tTOTPsecret
        self.faces_folder = "fcs/"      



    def mark_attendanceman(self, session: "AttendanceSession", name, status = "Present"):
        """
        Manually override a student's attendance status
 
        Parameters:

            -session:       the live AttendanceSession for the current class
            -name:      full name string matching the fcs/ filename stem
            -status:        "Present" | "Late" | "Absent" | "Excused"
        """
        session.manual_override(name, status)
 


    def search_student(self, query, session: "AttendanceSession"):
        """
        Returns filtered attendance records whose name contains `query`
        (case-insensitive)
        """
        q = query.lower()
        return [r for r in session.get_records() if q in r["name"].lower()]
 


    def validate_folder_path(self):
        """
        Raises FileNotFoundError if the faces folder does not exist.
        Teachers are responsible for enrolling faces, so validation
        lives here rather than inside FRC.
        """
        if not os.path.isdir(self.faces_folder):
            raise FileNotFoundError(f"Faces folder not found: {self.faces_folder}")
 



    def log_attendance(self, course, student: "Student",  attendance_status,  notes: str | None = None):
        """
        Appends one attendance row to the class CSV file
 
        Parameters:

            -course:        Course the student belongs to
            -student:       Student being logged
            -attendance_status:     "Present" | "Late" | "Absent"
            -notes:     optional free-text teacher note
        """
        output_dir = "Attendance Log/"
        formatted_date = datetime.now().strftime("%Y-%m-%d")
        output_file_name = (f"{output_dir}{course.class_name}{course.class_id}" f"{formatted_date}.csv")
        file_exists = os.path.exists(output_file_name)
        headers = ["First Name", "Last Name", "Attendance Status", "Notes"]
        data = [student.first_name, student.last_name, attendance_status, notes]
 
        # Ensure the output directory exists before any file operation.
        os.makedirs(output_dir, exist_ok=True)
 
        if file_exists:
            # File already has headers so just append the new data row.
            with open(output_file_name, "a", newline="") as file:
                csv.writer(file).writerow(data)
        else:
            # New file, write the header row first, then the data row.
            with open(output_file_name, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(headers)   
                writer.writerow(data)     
 
 































class AttendanceSession:
    """
    Tracks which students have been detected and marked present during one
    live class session.

        # Set of names already processed — prevents duplicate records.
                # Ordered record list.  Each entry is a dict:
        #   { "name": str, "time": str, "status": str }
            # Epoch second when the session started — used for late calculation.
        # Grace period in seconds for arithmetic comparison.
        # Manual overrides applied by the teacher: name → status.


    Parameters:

    -grace_period_minutes:      int Students arriving within this many minutes of session start are marked
    "Present". After that they are marked "Late".  Default is 5 min.
    """
 
    def __init__(self, grace_period_minutes: int = 5):
        self._seen = set()
        self._records = []
        self._start_time = time.time()
        self._grace_seconds = grace_period_minutes * 60.0
        self._overrides = {}
 


    def mark_present(self, name: str) -> None:
        """
        Called every frame for each non-unknown recognised face.
        Only acts on the *first* detection of a name per session.
        Subsequent calls are silently ignored via the O(1) set membership
        check, a student standing in frame for two minutes produces exactly
        one attendance record.
        Status is determined by comparing elapsed session time against the
        configured grace period
        """
        if name in self._seen:
            return   # already logged — cheapest possible early exit
 
        self._seen.add(name)
        elapsed = time.time() - self._start_time
        status = "Present" if elapsed <= self._grace_seconds else "Late"
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._records.append({"name": name, "time": timestamp, "status": status})
 


    def manual_override(self, name, status):
        """
        Teacher manually sets or changes a student's status.
        If the student was already auto-detected, their existing record is
        updated in-place.  If they were never detected (e.g. the teacher is
        marking someone Absent), a new record is created so it appears in
        the listbox and the export.
 
        Parameters:

            -name:      full name as it appears in the fcs/ filename stem
            -status:        "Present" | "Late" | "Absent" | "Excused"
        """
        self._overrides[name] = status
 
        # Update an existing record in-place.
        for record in self._records:
            if record["name"] == name:
                record["status"] = status
                return
 
        # No existing record. Insert one so the name appears in the UI.
        self._seen.add(name)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._records.append({"name": name, "time": timestamp, "status": status})
 
 

    def get_records(self):
        """
        Returns a shallow copy of the ordered record list.
        Each record is {"name": str, "time": str, "status": str}.
        Used by Teacher.search_student() and export_to_csv().
        """
        return list(self._records)



    def get_display_list(self) -> list[str]:
        """
        Returns formatted strings ready for the Tkinter Listbox (FR5).
        Format per row: "HH:MM:SS  | Present  |  John Smith"
        """
        return [f"{r['time']}  |  {r['status']:<8}|  {r['name']}"for r in self._records]
 


    def get_name_set(self):
        """
        Returns the set of all names seen this session.
        main.py uses this to decide whether the listbox needs refreshing.
        """
        return set(self._seen)
 
  

    def export_to_csv(self, course, output_dir = "Attendance Log/"):
        """
        Writes all session records to a CSV file and returns the file path.
        The filename encodes class name, ID, and today's date so that
        multiple sessions on the same day produce distinct files rather than
        overwriting each other.
 
        Parameters:
            -course:        Course object providing name / ID for the filename
            -output_dir:        directory to write into (created automatically if absent)
 
        Returns:
            str:        path of the written CSV file (relative to the project root)
        """
        os.makedirs(output_dir, exist_ok = True)
        formatted_date = datetime.now().strftime("%Y-%m-%d")
        filename = (f"{output_dir}{course.class_name}_{course.class_id}" f"_{formatted_date}.csv")
 
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Time Detected", "Status"])

            for record in self._records:
                writer.writerow([record["name"], record["time"], record["status"]])
 
        return filename
 