from django.utils.unittest.case import TestCase
from scheduler.models import SemesterSchedule, ScheduleItem
from uni_info.models import Semester, Section


class SemesterScheduleTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]

    def test_should_create(self):
        sem_schedule = SemesterSchedule(schedule_items=[])
        sem_schedule.semester = self.fall_2013_semester
        sem_schedule.save()

    def test_should_create_from_items(self):
        items = []
        sec = [Section.objects.all()[0]]
        items.append(ScheduleItem(sec))
        items.append(ScheduleItem(sec))
        sem_schedule = SemesterSchedule(schedule_items=items)
        sem_schedule.semester = self.fall_2013_semester
        sem_schedule.save()
