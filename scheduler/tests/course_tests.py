from django.test import TestCase
from uni_info.models import Course, Semester, Department


class CourseTest(TestCase):
    """
    Test class for Course configuration object
    """
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        """
        Setup common data needed in each unit test
        """
        self.fall_2013_semester = [sem for sem in Semester.objects.all()
                                   if sem.name == 'Fall 2013'][0]
        self.department = Department.objects.all()[0]

    def test_should_find_by_id(self):
        """
        Test that we can find by primary key, check attributes
        """
        course = Course.objects.get(id=1)
        self.assertIsNotNone(course)
        self.assertEqual('ELEC', course.course_letters)
        self.assertEqual('275', course.course_numbers)
        self.assertEqual(1, course.openness)

    def test_should_create_course(self):
        """
        Test that we can create a course for a department, check existence
        """
        course = Course()
        course.department = self.department
        course.openness = 0
        course.save()
        self.assertIsNotNone(course.id)
        check = Course.objects.get(id=course.id)
        self.assertIsNotNone(check)

    def test_should_update_course(self):
        """
        Test that we can update an attribute for a course
        """
        course = Course.objects.all()[0]
        course_id = course.id
        course.openness = 1
        course.save()
        check = Course.objects.get(id=course_id)
        self.assertEqual(1, check.openness)

    def test_should_delete_course(self):
        """
        Test that we can delete a course and that afterwards cannot be found
        """
        course = Course.objects.get(id=2)
        self.assertIsNotNone(course)
        course.delete()
        check = False
        try:
            Course.objects.get(id=2)
        except Course.DoesNotExist:
            check = True

        self.assertTrue(check)

    def test_should_filter_by_course_letters(self):
        """
        Test we can find by course letters, check each value after to ensure correctness
        """
        soen_list = Course.objects.filter(course_letters='SOEN')
        self.assertIsNotNone(soen_list)
        self.assertEqual(18, len(soen_list))
        for c in soen_list:
            self.assertEqual("SOEN", c.course_letters)

    def test_should_filter_by_name_and_section(self):
        """
        Test we can find with regular expression and can group into semesters
        """
        course_list = Course.search_by_regex(r'SOEN')
        semester_list = [4]
        sections_by_semester = []

        for course in course_list:
            for semester in semester_list:
                sections_by_semester.extend(course.get_sections_for_semester(semester))

        self.assertIsNotNone(sections_by_semester)
