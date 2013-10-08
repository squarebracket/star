from django.db import models
from scheduler.models.course import Course
from scheduler.models.semester import Semester


class Section(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    course = models.ForeignKey(Course)
    semester_year = models.ForeignKey(Semester, null=True)

    def is_not_full(self):
        return len(self.studentrecordentry_set.all()) < self.capacity

    def __unicode__(self):
        return str(self.course.name) + " " + str(self.name)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'