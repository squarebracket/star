from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from scheduler.choices import GENDER_CHOICES


class StarUser(AbstractUser):
    date_of_birth = models.DateField('date of birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    errorList = []
    infoList = []
    custom_objects = UserManager()

    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['date_of_birth']

    class Meta:
        def __init__(self):
            pass

        app_label = 'auth'