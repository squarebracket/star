from django.db import models
from scheduler.models.professor import Professor
from scheduler.models.schedule_item import ScheduleItem


class Lecture(ScheduleItem):
    professor = models.ForeignKey(Professor)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'