from django.db import models
from uni_info.models.faculty import Faculty
from user_stuff.models.star_user import StarUser


class Registrar(StarUser):
    faculty = models.ForeignKey(Faculty)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "registrar"
        app_label = 'user_stuff'
