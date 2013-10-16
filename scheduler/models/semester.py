from django.db import models
from scheduler.choices import SEMESTER_CHOICES


class Semester(models.Model):
    year = models.IntegerField(default=0)
    period = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    is_open = models.BooleanField('is open')

    @property
    def name(self):
        return self.get_period_display() + " " + str(self.year)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'