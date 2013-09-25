from django.utils.unittest.case import TestCase
from scheduler.models import AcademicInstitution, Student, Course
from scheduler.services import StudentService


class StudentServiceTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def test_should_register_course_for_student(self):
        studentService = StudentService()
        test_student = Student.objects.get_by_natural_key("student_user1")
        new_course = Course.objects.get(name="SOEN 341")

        self.assertIsNotNone(test_student)
        self.assertIsNotNone(new_course)

        studentService.RegisterStudentToCourse(test_student, new_course)

        self.assertEqual(0, len(test_student.errorList))

        old_course = test_student.studentrecord.studentrecordentry_set.all()[0].course

        studentService.RegisterStudentToCourse(test_student, old_course)

        self.assertEqual(1, len(test_student.errorList))
        print(AcademicInstitution.objects.all())
