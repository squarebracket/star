from django.db import models
from scheduler.choices import PROGRAM_TYPE_CHOICES
from uni_info.models.faculty import Faculty


class AcademicProgram(models.Model):
    name = models.CharField(max_length=256)
    faculty = models.ForeignKey(Faculty)
    total_required_credits = models.IntegerField(default=0)
    required_gpa = models.DecimalField(default=0.00, decimal_places=2,
                                       max_digits=10)
    type = models.CharField(max_length=1, choices=PROGRAM_TYPE_CHOICES)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'

