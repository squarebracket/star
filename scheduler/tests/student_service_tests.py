from django.utils.unittest.case import TestCase
from scheduler.models import AcademicInstitution


class StudentServiceTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def should_register_course_for_student(self):
        print(AcademicInstitution.objects.all())
