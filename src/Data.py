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

class Student:
    
    #Constructors
    def __init__(self, first_name, last_name, stu_email, face_scan_data, last_picture):
        self.first_name = first_name
        self.last_name = last_name
        self.stu_email = stu_email
        self.face_scan_data = face_scan_data
        self.last_picture = last_picture

        attendance_days =   [
            
                {

                }
                            
                            ]
        
        
        def sent_attendance_request():
            pass

class Course:
        
    def __init__(self, name, class_id, class_name, assigned_teacher, days, time):
        self.name = name
        self.class_id = class_id
        self.class_name = class_name
        self.assigned_teacher = assigned_teacher
        self.days = days
        self.time = time

class Teacher:
    
    def __init__(self, tfirst_name, tlast_name, teacher_id, teacher_TOTP_secret):
        self.tfirst_name = tfirst_name
        self.tlast_name = tlast_name
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
        
