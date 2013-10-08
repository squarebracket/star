from django.db import models
from scheduler.models.schedule_item import ScheduleItem
from scheduler.models.student import Student


class Tutorial(ScheduleItem):
    name = models.CharField(max_length=20)
    tutor = models.ForeignKey(Student)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'