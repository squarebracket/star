from django.db import models
from scheduler.models.academic_institution import AcademicInstitution


class Faculty(models.Model):
    name = models.CharField(max_length=256)
    university = models.ForeignKey(AcademicInstitution)
    code = models.PositiveSmallIntegerField(unique=True)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'