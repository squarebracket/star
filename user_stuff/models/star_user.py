from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class StarUser(AbstractUser):

    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    date_of_birth = models.DateField('date of birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    error_list = []
    info_list = []
    custom_objects = UserManager()

    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['date_of_birth']

    @property
    def has_errors(self):
        return len(self.error_list) > 0

    def clear_error_list(self):
        del self.error_list[:]

    def clear_info_list(self):
        del self.info_list[:]

    class Meta:
        def __init__(self):
            pass

        app_label = 'auth'