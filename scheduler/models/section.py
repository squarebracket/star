from django.db import models
from scheduler.models.course import Course
from scheduler.models.semester import Semester
from itertools import chain


class Section(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    course = models.ForeignKey(Course)
    semester_year = models.ForeignKey(Semester, null=True)

    def is_not_full(self):
        return len(self.studentrecordentry_set.all()) < self.capacity

    def conflicts_with(self, section):

        for my_item in self.all_schedule_items:
            for test_item in section.all_schedule_items:
                if my_item.conflicts_with(test_item):
                    return True
        return False

    @property
    def all_schedule_items(self):
        result_list = list(chain(self.lectures, self.labs, self.tutorials))
        return result_list

    @property
    def lectures(self):
        from scheduler.models import Lecture
        return Lecture.objects.filter(section=self)

    @property
    def labs(self):
        from scheduler.models import Lab
        return Lab.objects.filter(section=self)

    @property
    def tutorials(self):
        from scheduler.models import Tutorial
        return Tutorial.objects.filter(section=self)

    def __unicode__(self):
        return str(self.course.name) + " " + str(self.name) + " " + str(self.semester_year)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'