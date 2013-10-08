from django.db import models
from scheduler.models.faculty import Faculty
from scheduler.models.star_user import StarUser


class Professor(StarUser):
    faculty = models.ForeignKey(Faculty)

    class Meta:
        def __init__(self):
            pass
        verbose_name = "professor"
        app_label = 'scheduler'