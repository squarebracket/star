from django.db import models
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser


class Director(StarUser):
    program = models.ForeignKey(AcademicProgram)

    class Meta:
        verbose_name = "director"

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'