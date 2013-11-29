from django.utils.unittest.case import TestCase
from scheduler.models import ScheduleGenerator
from uni_info.models import Semester, Course


class ScheduleGeneratorTest(TestCase):
    """
    Test class for schedule generator, try different courses
    """
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        """
        Setup common data needed in each unit test
        """
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]

    def test_should_generate_empty_schedule(self):
        """
        Test generator does not crash with empty list as edge case
        """
        course_list = []
        generator = ScheduleGenerator(course_list, self.fall_2013_semester)
        result = generator.generate_schedules()
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    def test_should_generate_with_1_course(self):
        """
        Test generator with only 1 course as edge case
        """
        soen341 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '341'][0]

        course_list = [soen341]

        generator = ScheduleGenerator(course_list, self.fall_2013_semester)
        result = generator.generate_schedules()

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))

    def test_should_generate_schedule_for_2_course(self):
        """
        Test generator with more than 1 course
        """
        soen341 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '341'][0]

        soen287 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '287'][0]

        course_list = [soen287, soen341]

        generator = ScheduleGenerator(course_list, self.fall_2013_semester)
        result = generator.generate_schedules()

        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))

    def test_should_not_generate_schedule_for_3_course_conflict(self):
        """
        Test generator with three conflicting courses
        """
        soen341 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '341'][0]

        soen342 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '342'][0]

        soen287 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '287'][0]

        course_list = [soen287, soen341, soen342]

        generator = ScheduleGenerator(course_list, self.fall_2013_semester)
        result = generator.generate_schedules()

        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    def test_should_generate_schedule_for_3_course_no_conflict(self):
        """
        Test generator with three courses that has no conflicts
        """
        soen341 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '341'][0]

        soen343 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '343'][0]

        soen287 = [s for s in Course.objects.all() if
                   s.course_letters == 'SOEN' and
                   s.course_numbers == '287'][0]

        course_list = [soen287, soen341, soen343]

        generator = ScheduleGenerator(course_list, self.fall_2013_semester)
        result = generator.generate_schedules()

        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))