from django.db import models
from scheduler.models.faculty import Faculty
from scheduler.models.star_user import StarUser


class Registrar(StarUser):
    faculty = models.ForeignKey(Faculty)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "registrar"
        app_label = 'scheduler'
