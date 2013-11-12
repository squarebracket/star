from django.db import models
from django.core import serializers
from uni_info.models import Semester
from scheduler.models.schedule_item import ScheduleItem
import cPickle


class SemesterSchedule(models.Model):

    pickled_items = models.TextField()
    semester = models.ForeignKey(Semester)
    schedule_items = []

    def __init__(self, *args, **kwargs):
        keep_track = None
        # print args
        if 'schedule_items' in kwargs:
            keep_track = kwargs['schedule_items']
            del kwargs['schedule_items']
        super(SemesterSchedule, self).__init__(*args, **kwargs)
        if keep_track:
            self.schedule_items = keep_track
            self.semester = keep_track[0].semester
        elif self.pickled_items != '':
                self.schedule_items = cPickle.loads(str(self.pickled_items))

    def save(self, *args, **kwargs):
        self.pickled_items = cPickle.dumps(self.schedule_items)
        try:
            self.semester
        except Semester.DoesNotExist as e:
            if len(self.schedule_items) > 0:
                self.semester = self.schedule_items[0].semester
            else:
                raise e
        super(SemesterSchedule, self).save(*args, **kwargs)

    def conflicts_with(self, check_against_item):
        for schedule_item in self.schedule_items:
            if schedule_item.conflicts_with(check_against_item):
                return True
        return False

    def add_schedule_item(self, schedule_item):
        if self.conflicts_with(schedule_item):
            return False
        else:
            self.schedule_items.append(schedule_item)
            return True

    @property
    def sections(self):
        sections = []
        for schedule_item in self.schedule_items:
            for section in schedule_item.sections:
                sections.append(section)
        return sections

    class Meta:
        def __init__(self):
            pass

        def __str__(self):
            return self.semester

        app_label = 'scheduler'


class Schedule():
    def __init__(self):
        self.schedule_by_semester = {}
        """:type :dict[Semester, SemesterSchedule]"""
        return

    def add_schedule_item(self, item, semester):
        """
        Adds a schedule item to the list for the semester
        @type item:ScheduleItem
        @type semester:Semester
        """
        if semester not in self.schedule_by_semester:
            self.schedule_by_semester[semester] = SemesterSchedule()

        self.schedule_by_semester[semester].schedule_items.append(item)

    # def add_section(self, section):
    #     """
    #     Add all the lectures, tutorials and labs for a section
    #     to the schedule
    #     @type section:Section
    #     """
    #     for sec in section.section_tree:
    #         self.add_schedule_item(sec, section.semester_year)

    def add_section(self, section):
        """
        Add all the lectures, tutorials and labs for a section
        to the schedule
        @type section:Section
        """
        for sec in section.section_tree_from_here:
            self.add_schedule_item(sec, section.semester_year)

    def has_no_conflict_with(self, section):
        """
        Checks if the schedule is in conflict with the section
        @type section:Section
        """
        if section.semester_year not in self.schedule_by_semester:
            return True
        else:
            return self.schedule_by_semester[section.semester_year].has_no_conflict_with(section)

    def clear(self):
        self.schedule_by_semester.clear()

    @property
    def semester_schedules(self):
        return self.schedule_by_semester.values()