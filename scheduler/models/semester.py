from django.db import models
from scheduler.choices import SEMESTER_CHOICES


class Semester(models.Model):
    year = models.IntegerField(default=0)
    period = models.CharField(max_length=2, choices=SEMESTER_CHOICES)

    def __unicode__(self):
        return str(self.period) + " " + str(self.year)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'