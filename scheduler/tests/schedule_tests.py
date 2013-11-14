from django.test import TestCase
from scheduler.models import Schedule
from uni_info.models import Section


class ScheduleTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.schedule = Schedule()

    def test_should_add_section_to_schedule(self):
        all_section = Section.objects.all()

        soen_341 = [s for s in all_section if s.course.name == "SOEN 341" and s.semester_year.name == "Fall 2013"]
        self.assertEqual(3, len(soen_341))
        self.schedule.add_section(soen_341[0])

        #Check we have something for a semester
        #self.assertEqual(1, len(self.schedule.semester_schedules))

        #Check we have an item in that semester
        #self.assertEqual(1, len(self.schedule.semester_schedules[0].schedule_items))

