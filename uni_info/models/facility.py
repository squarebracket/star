from datetime import time
from django.db import models
from uni_info.models.building import Building


class Facility(models.Model):
    name = models.CharField(max_length=20, unique=True)
    building = models.ForeignKey(Building)
    capacity = models.IntegerField(default=0)
    available_start_time = models.TimeField('available start time',
                                            default=time(hour=8, minute=0))
    available_end_time = models.TimeField('available end time',
                                          default=time(hour=22, minute=0))

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'