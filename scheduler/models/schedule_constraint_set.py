from django.db import models
from user_stuff.models.student import Student


class ScheduleConstraintSet(models.Model):
    name = models.CharField(max_length=20)
    student = models.ForeignKey(Student, null=True)

    @property
    def sections(self):
        return self.scheduleconstraint_set.all()

    def __iter__(self):
        for item in self.scheduleconstraint_set.all():
            yield item

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'