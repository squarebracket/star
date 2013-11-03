from django.db import models
from user_stuff.models.student import Student


class ScheduleConstraintSet(models.Model):
    name = models.CharField(max_length=20)
    student = models.ForeignKey(Student)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'