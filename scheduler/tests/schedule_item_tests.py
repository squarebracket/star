from datetime import time
from django.utils.unittest.case import TestCase
from scheduler.models import ScheduleItem
from uni_info.models import Semester, Section, Course


class ScheduleItemTest(TestCase):
    """
    Test class for Schedule Item conflict testing
    """
    fixtures = ['/scheduler/fixtures/initial_data.json']

    def setUp(self):
        """
        Setup common data used in each unit test
        """
        self.fall_2013_semester = [sem for sem in Semester.objects.all() if sem.name == 'Fall 2013'][0]
        self.course_1 = Course.objects.get(id=1)
        self.section_1 = Section.objects.get(id=1)
        self.section_2 = Section.objects.get(id=2)
        self.section_3 = Section.objects.get(id=3)
        self.section_7_to_9 = Section(start_time=time(hour=7),
                                      end_time=time(hour=9),
                                      course=self.course_1,
                                      days="M")
        self.section_8_to_10 = Section(start_time=time(hour=8),
                                       end_time=time(hour=10),
                                       course=self.course_1,
                                       days="M")
        self.section_10_to_12 = Section(start_time=time(hour=10),
                                        end_time=time(hour=12),
                                        course=self.course_1,
                                        days="M")
        self.section_7_to_12 = Section(start_time=time(hour=7),
                                       end_time=time(hour=12),
                                       course=self.course_1,
                                       days="M")

    def test_should_not_conflict_if_before(self):
        """
        Test item 1 is before item 2
        """
        list_1 = [self.section_7_to_9]
        list_2 = [self.section_10_to_12]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertFalse(chk)

    def test_should_not_conflict_if_after(self):
        """
        Test item 2 is after item 1
        """
        list_1 = [self.section_7_to_9]
        list_2 = [self.section_10_to_12]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_2.conflicts_with(item_1)
        self.assertFalse(chk)

    def test_should_conflict_if_straddle_other_start(self):
        """
        Test item 1 straddle item 2 start
        """
        list_1 = [self.section_7_to_9]
        list_2 = [self.section_8_to_10]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertTrue(chk)

    def test_should_conflict_if_straddle_other_end(self):
        """
        Test item 2 straddle item 1 end
        """
        list_1 = [self.section_7_to_9]
        list_2 = [self.section_8_to_10]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_2.conflicts_with(item_1)
        self.assertTrue(chk)

    def test_should_conflict_if_with_in(self):
        """
        Test item 2 within item 1 end
        """
        list_1 = [self.section_7_to_12]
        list_2 = [self.section_8_to_10]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_2.conflicts_with(item_1)
        self.assertTrue(chk)

    def test_should_conflict_if_cover(self):
        """
        Test item 1 covers item 2 end
        """
        list_1 = [self.section_7_to_12]
        list_2 = [self.section_8_to_10]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertTrue(chk)

    def test_should_not_find_conflict_with_different_courses(self):
        """
        Test no conflict with different courses
        """
        list_1 = [self.section_1, self.section_2]
        list_2 = [self.section_3]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertFalse(chk)

    def test_should_find_conflict_with_same_course(self):
        """
        Test conflict with same courses
        """
        soen341s = [s for s in Section.objects.all() if
                    s.course.course_letters == 'SOEN' and
                    s.course.course_numbers == '341']
        list_1 = [soen341s[0], soen341s[1]]
        list_2 = [soen341s[0]]
        item_1 = ScheduleItem(section_list=list_1)
        item_2 = ScheduleItem(section_list=list_2)

        chk = item_1.conflicts_with(item_2)
        self.assertTrue(chk)