"""
Sebastian Olah
Muhammad Usman
Josh Rudnick

UML Diagram Assignment
CSIII
Mr.Ding

Starter code for Data
"""

#Modules
import face_recognition
import numpy

#Classes

class Course:
        
    def __init__(self, name, class_id, class_name, assigned_teacher, days, time):
        self.name = name
        self.class_id = class_id
        self.class_name = class_name
        self.assigned_teacher = assigned_teacher
        self.days = days
        self.time = time

        

class Student(Course):
    
    #Constructors
    def __init__(self, fname, lname, stu_email, face_scan_data, last_picture):
        self.first_name = fname
        self.last_name = lname
        self.stu_email = stu_email
        self.face_scan_data = face_scan_data
        self.last_picture = last_picture
        Course.__init__(self, name=None, class_id=None, class_name=None, assigned_teacher=None, days=None, time=None)

        self.attendance_days =   [
            
                {

                }
                            
                            ]
        


class Teacher:
    
    def __init__(self, tfname, tlname, teacher_id, tTOTPsecret):
        self.tfirst_name = tfname
        self.tlast_name = tlname
        self.teacher_id = teacher_id

        def verify_teacher():
            pass

        def view_class_dashboard():
            pass

        def mark_attendanceman():
            pass

        def search_student():
            pass

        def manage_class():
            pass
        
