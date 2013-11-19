from django.db import models


class Semester(models.Model):

    # "enum" of semesters
    FALL = 'F'
    WINTER = 'W'
    YEAR_LONG = 'Y'
    SUMMER_1 = 'S1'
    SUMMER_2 = 'S2'

    SEMESTER_CHOICES = (
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (YEAR_LONG, 'Fall/Winter'),
        (SUMMER_1, 'Summer 1'),
        (SUMMER_2, 'Summer 2'),
    )

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

        app_label = 'uni_info'