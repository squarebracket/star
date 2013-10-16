from django.db import models
from scheduler.choices import DAY_OF_WEEK_CHOICES
from scheduler.models.facility import Facility
from scheduler.models.section import Section


class ScheduleItem(models.Model):
    location = models.ForeignKey(Facility)
    start_time = models.TimeField('start time')
    end_time = models.TimeField('end time')
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES)
    section = models.ForeignKey(Section)

    def conflits_with(self, other_item):
        return False

    def __unicode__(self):
        return "%s from %s to %s on %s" % (self.location, self.start_time,
                                           self.end_time, self.day_of_week)


    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'