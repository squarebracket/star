from django.db import models
from scheduler.models.course import Course


class Corequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_c")
    corequisite_course = models.ForeignKey(Course,
                                           related_name="corequisite_course")

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'