from django.utils.unittest.case import TestCase
from scheduler.models import ScheduleGenerator
from uni_info.models import Semester, Course


class ScheduleGeneratorTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]

    def test_should_generate_schedule_for_2_course(self):
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