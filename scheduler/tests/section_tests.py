from django.utils.unittest.case import TestCase
from uni_info.models import Semester, Section, Course


class SectionTest(TestCase):
    """
    Test class for Section configuration objects
    """
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        """
        Set up common data needed in each unit test
        """
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]

    def test_should_find_by_id(self):
        section = Section.objects.get(id=1)
        self.assertEqual(24, section.course_id)
        self.assertEqual(4, section.semester_year_id)
        self.assertEqual('IE', section.name)
        self.assertEqual(6, section.sec_type)
        self.assertIsNotNone(section)

    def test_should_create_section(self):
        """
        Test that we can crete a section for a course in a semester
        """
        course = Course.objects.all()[0]
        section = Section()
        section.course = course
        section.sec_type = 1
        section.semester_year = self.fall_2013_semester
        section.save()
        self.assertIsNotNone(section.id)

    def test_should_update_section(self):
        """
        Test that we can update the attribute of a section
        """
        section = Section.objects.get(id=2)
        self.assertEqual(0, section.capacity)
        section.capacity = 100
        section.save()
        check = Section.objects.get(id=2)
        self.assertEqual(100, check.capacity)

    def test_should_delete_section(self):
        """
        Test that we can delete a section
        """
        section = Section.objects.get(id=3)
        self.assertIsNotNone(section)
        section.delete()
        check = False
        try:
            Section.objects.get(id=3)
        except Section.DoesNotExist:
            check = True
        self.assertTrue(check)

    def test_should_filter_by_type(self):
        """
        Test that we can find by type of section
        """
        section_list = Section.objects.filter(sec_type=6)
        self.assertIsNotNone(section_list)

        for s in section_list:
            self.assertEqual(6, s.sec_type)
