from django.db import models
from uni_info.models.academic_institution import AcademicInstitution
from uni_info.models.faculty import Faculty


class Department(models.Model):
    name = models.CharField(max_length=256)
    code = models.PositiveSmallIntegerField()
    faculty = models.ForeignKey(Faculty)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'