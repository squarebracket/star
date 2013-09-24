from django.utils.unittest.case import TestCase
from scheduler.models import AcademicInstitution, Student, Course
from scheduler.services import StudentService


class StudentServiceTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def test_should_register_course_for_student(self):
        studentService = StudentService()
        test_student = Student.objects.get_by_natural_key("testuser")
        course = Course.objects.get(name="SOEN 341")

        self.assertIsNotNone(test_student)
        self.assertIsNotNone(course)

        studentService.RegisterStudentToCourse(test_student, course)

        self.assertEqual(0, len(test_student.errorList))

        print(AcademicInstitution.objects.all())
