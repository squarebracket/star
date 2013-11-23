from django.utils.unittest.case import TestCase
from scheduler.models import ScheduleItem
from uni_info.models import Semester, Section


class ScheduleItemTest(TestCase):
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]
        self.section_1 = Section.objects.get(id=1)
        self.section_2 = Section.objects.get(id=2)
        self.section_3 = Section.objects.get(id=3)

    def test_should_create_and_should_not_find_conflict(self):
        list_1 = [self.section_1, self.section_2]
        list_2 = [self.section_3]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertFalse(chk)

    def test_should_create_and_should_find_conflict(self):
        soen341s = [s for s in Section.objects.all() if
                    s.course.course_letters == 'SOEN' and
                    s.course.course_numbers == '341']
        list_1 = [soen341s[0], soen341s[1]]
        list_2 = [soen341s[0]]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertTrue(chk)