from django.utils.unittest.case import TestCase
from uni_info.models import Semester, Section, Course


class SectionTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]

    def test_should_create(self):
        course = Course.objects.all()[0]
        sec = Section()
        sec.course = course
        sec.sec_type = 1
        sec.semester_year = self.fall_2013_semester
        sec.save()

    def test_should_find_by_id(self):
        sec = Section.objects.filter(id=1)
        self.assertIsNotNone(sec)