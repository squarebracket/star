from django.db import models
from uni_info.models.academic_program import AcademicProgram
from user_stuff.models.star_user import StarUser


class Director(StarUser):
    program = models.ForeignKey(AcademicProgram)

    class Meta:
        verbose_name = "director"

    class Meta:
        def __init__(self):
            pass

        app_label = 'user_stuff'