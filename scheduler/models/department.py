from django.db import models
from scheduler.models.academic_institution import AcademicInstitution
from scheduler.models.faculty import Faculty


class Department(models.Model):
    name = models.CharField(max_length=256)
    code = models.PositiveSmallIntegerField(unique=True)
    faculty = models.ForeignKey(Faculty)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'