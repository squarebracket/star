from django.db import models
from scheduler.models.course import Course


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_p")
    prerequisite_course = models.ForeignKey(Course,
                                            related_name="prerequisite_course")

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'