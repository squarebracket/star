from django.db import models
from scheduler.choices import DAY_OF_WEEK_CHOICES, TIME_OF_DAY_CHOICES
from scheduler.models.schedule_constraint_set import ScheduleConstraintSet


class ScheduleConstraint(models.Model):
    constraint_set = models.ForeignKey(ScheduleConstraintSet)
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES)
    time_of_day = models.CharField(max_length=1, choices=TIME_OF_DAY_CHOICES)
    course_name = models.CharField(max_length=20)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'