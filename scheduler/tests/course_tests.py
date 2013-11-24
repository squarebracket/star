from django.test import TestCase
from uni_info.models import Course, Semester, Department


class CourseTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]
        self.department = Department.objects.all()[0]

    def test_should_find_by_id(self):
        c = Course.objects.get(id=1)
        self.assertIsNotNone(c)
        self.assertEqual('ELEC', c.course_letters)
        self.assertEqual('275', c.course_numbers)
        self.assertEqual(1, c.openness)

    def test_should_create_course(self):
        c = Course()
        c.department = self.department
        c.openness = 0
        c.save()
        self.assertIsNotNone(c.id)

    def test_should_update_course(self):
        c = Course.objects.all()[0]
        course_id = c.id
        c.openness = 1
        c.save()
        check = Course.objects.get(id=course_id)
        self.assertEqual(1, check.openness)

    def test_should_delete_course(self):
        c = Course.objects.get(id=2)
        self.assertIsNotNone(c)
        c.delete()
        check = False
        try:
            Course.objects.get(id=2)
        except Course.DoesNotExist:
            check = True

        self.assertTrue(check)

    def test_should_filter_by_course_letters(self):
        soen_list = Course.objects.filter(course_letters='SOEN')
        self.assertIsNotNone(soen_list)
        self.assertEqual(18, len(soen_list))

    def test_should_filter_by_name_and_section(self):
        course_list = Course.search_by_regex(r'SOEN')
        semester_list = [4]
        sections_by_semester = []

        for course in course_list:
            for semester in semester_list:
                sections_by_semester.extend(course.get_sections_for_semester(semester))

        self.assertIsNotNone(sections_by_semester)
