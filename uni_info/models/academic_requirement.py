from django.db import models
from uni_info.models.academic_program import AcademicProgram
from uni_info.models.course import Course


class AcademicRequirement(models.Model):
    academic_program = models.ForeignKey(AcademicProgram)
    name = models.CharField(max_length=256)
    required_credits = models.IntegerField(default=0)
    allowable_courses = models.ManyToManyField(Course)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'