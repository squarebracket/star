from django.utils.unittest.case import TestCase
from scheduler.models import *
from scheduler.services import RegistrationService

import logging


class RegistrationServiceTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        #Find our test student
        self.student = Student.objects.get_by_natural_key("student_user_1")
        #Create our service for testing
        self.studentService = RegistrationService()

    def test_should_register_course_for_student(self):
        #Find the first course soen 341
        soen341 = Course.objects.get(name="SOEN 341")

        #Check that both are not null
        self.assertIsNotNone(self.student)
        self.assertIsNotNone(soen341)

        #Record the number of courses registered to this student
        current_student_registration_count = len(self.student.registration_set.all())
        #Register the student to the course
        self.studentService.RegisterStudentToCourse(self.student, soen341)
        #Check that we successfully registered for the course by count + 1
        self.assertEqual(current_student_registration_count + 1, len(self.student.registration_set.all()))
        #Check that there is no error reported
        self.assertEqual(0, len(self.student.errorList))

    def test_should_not_register_course_for_student_if_already_taken(self):
        #Record the number of courses registered to this student
        current_student_registration_count = len(self.student.registration_set.all())

        #Find a ENGR202 which the student has already taken
        student_records = [sre.course for sre in self.student.studentrecord.studentrecordentry_set.all()
                           if sre.course.name == "ENGR 202"]

        engr202 = student_records[0]
        self.assertIsNotNone(engr202)
        #Try to register the student to this course
        self.studentService.RegisterStudentToCourse(self.student, engr202)
        #Check that an error has occured
        self.assertEqual(1, len(self.student.errorList))
        #Check for specific error message
        self.assertEqual(RegistrationService.COURSE_ALREADY_TAKEN_ERROR_MSG, self.student.errorList[0])
        #Check and make sure registration count has not changed
        self.assertEqual(current_student_registration_count, len(self.student.registration_set.all()))
        del self.student.errorList[:]

    def test_should_not_register_course_if_no_section_open(self):
        #Record the number of courses registered to this student
        current_student_registration_count = len(self.student.registration_set.all())

        elec275 = Course.objects.get(name="ENGR 213")
        self.assertIsNotNone(elec275)
        #Try to register the student to this course
        self.studentService.RegisterStudentToCourse(self.student, elec275)
        #Check that an error has occured
        self.assertEqual(1, len(self.student.errorList))
        #Check for specific error message
        self.assertEqual(RegistrationService.NO_SECTION_AVAILABLE_ERROR_MSG, self.student.errorList[0])
        #Check and make sure registration count has not changed
        self.assertEqual(current_student_registration_count, len(self.student.registration_set.all()))
        del self.student.errorList[:]

    # def test_should_not_register_course_if_pre_req_not_fullfilled(self):
    #     #Create the Student Service
    #     studentService = StudentService()
    #
    #     #Find our test student
    #     student = Student.objects.get_by_natural_key("student_user_1")
    #     #Record the number of courses registered to this student
    #     current_student_registration_count = len(student.registration_set.all())
    #
    # def test_should_be_put_on_wait_list_if_sections_are_full(self):
    #     #Create the Student Service
    #     studentService = StudentService()
    #
    #     #Find our test student
    #     student = Student.objects.get_by_natural_key("student_user_1")
    #     #Record the number of courses registered to this student
    #     current_student_registration_count = len(student.registration_set.all())
