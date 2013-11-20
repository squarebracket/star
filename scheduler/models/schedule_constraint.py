from django.db import models
from scheduler.choices import DAY_OF_WEEK_CHOICES, TIME_OF_DAY_CHOICES
from scheduler.models.schedule_constraint_set import ScheduleConstraintSet
from scheduler.models import ScheduleItem
from datetime import time


class ScheduleConstraint(models.Model):
    """
    Mimics a section for checking against :model:`scheduler.ScheduleItem`s
    """

    MORNING_START = time(0, 0)
    MORNING_END = time(12, 00)

    AFTERNOON_START = time(12, 01)
    AFTERNOON_END = time(17, 30)

    EVENING_START = time(17, 31)
    EVENING_END = time(23, 59)

    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.CharField(max_length=7)
    course = None
    con_set = models.ForeignKey(ScheduleConstraintSet)

    @property
    def sections(self):
        return [self]

    #def __init__(self, days, start_time, end_time):
    #    self.start_time = start_time
    #    self.end_time = end_time
    #    self.days = days
    #    self.course = None

    class Meta:
        app_label = 'scheduler'
