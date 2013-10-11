from django.test import TestCase
from scheduler.models import Student


class StudentTest(TestCase):

    def test_should_get_registered_courses(self):
        student_one = Student.objects.get_by_natural_key('student_user_1')
        self.assertEquals(2, len(student_one.registered_courses))

    def test_should_get_completed_courses(self):
        student_one = Student.objects.get_by_natural_key('student_user_1')
        self.assertEquals(3, len(student_one.completed_courses))
