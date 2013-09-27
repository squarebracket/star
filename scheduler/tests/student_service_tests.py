from django.utils.unittest.case import TestCase
from scheduler.models import *
from scheduler.services import StudentService

import logging


class StudentServiceTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def test_should_register_course_for_student(self):
        #Create the Student Service
        studentService = StudentService()

        #Find our test student
        student = Student.objects.get_by_natural_key("student_user_1")
        #Find the first course soen 341
        soen341 = Course.objects.get(name="SOEN 341")

        #Check that both are not null
        self.assertIsNotNone(student)
        self.assertIsNotNone(soen341)

        #Record the number of courses registered to this student
        current_student_registration_count = len(student.registration_set.all())
        #Register the student to the course
        studentService.RegisterStudentToCourse(student, soen341)
        #Check that we successfully registered for the course by count + 1
        self.assertEqual(current_student_registration_count + 1, len(student.registration_set.all()))
        #Check that there is no error reported
        self.assertEqual(0, len(student.errorList))

    def test_should_not_register_course_for_student_if_already_taken(self):
        #Create the Student Service
        studentService = StudentService()

        #Find our test student
        student = Student.objects.get_by_natural_key("student_user_1")
        #Record the number of courses registered to this student
        current_student_registration_count = len(student.registration_set.all())

        #Find a ENGR202 which the student has already taken
        student_records = [sre.course for sre in student.studentrecord.studentrecordentry_set.all()
                           if sre.course.name == "ENGR 202"]


        engr202 = student_records[0]
        self.assertIsNotNone(engr202)
        #Try to register the student to this course
        studentService.RegisterStudentToCourse(student, engr202)
        #Check that an error has occured
        self.assertEqual(1, len(student.errorList))
        #Check for specific error message
        self.assertEqual(StudentService.COURSE_ALREADY_TAKEN_ERROR_MSG, student.errorList[0])
        #Check and make sure registration count has not changed
        self.assertEqual(current_student_registration_count, len(student.registration_set.all()))

    def test_should_not_register_course_if_no_section_open(self):
        #Create the Student Service
        studentService = StudentService()

        #Find our test student
        student = Student.objects.get_by_natural_key("student_user_1")
        #Record the number of courses registered to this student
        current_student_registration_count = len(student.registration_set.all())

        elec275 = Course.objects.get(name="ENGR 213")
        self.assertIsNotNone(elec275)
        #Try to register the student to this course
        studentService.RegisterStudentToCourse(student, elec275)
        #Check that an error has occured
        self.assertEqual(1, len(student.errorList))
        #Check for specific error message
        self.assertEqual(StudentService.NO_SECTION_AVAILABLE_ERROR_MSG, student.errorList[0])
        #Check and make sure registration count has not changed
        self.assertEqual(current_student_registration_count, len(student.registration_set.all()))