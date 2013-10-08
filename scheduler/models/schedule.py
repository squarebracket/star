from django.db import models
from scheduler.models.schedule_constraint_set import ScheduleConstraintSet
from scheduler.models.schedule_item import ScheduleItem


class CalculatedSchedule(models.Model):
    constraint_set = models.OneToOneField(ScheduleConstraintSet)
    items = models.ManyToManyField(ScheduleItem)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'