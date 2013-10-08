from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser


class Student(StarUser):
    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    @property
    def registered_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "R"]

    @property
    def completed_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "C"]

    def __unicode__(self):
        return "id#%s (%s %s)" % (self.student_identifier, self.first_name,
                                  self.last_name)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "student"
        app_label = 'scheduler'