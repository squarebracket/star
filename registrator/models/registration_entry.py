from django.db import models
from uni_info.models import Section
from user_stuff.models import StarUser


class RegistrationEntry(models.Model):

    """
    A single entry for a registration action performed by a user.
    """

    REGISTER = 1
    DROP = 2
    CHANGE_SECTION = 3

    ACTION_CHOICES = (
        (REGISTER, "Register"),
        (DROP, "Drop"),
        (CHANGE_SECTION, "Change of section"),
    )

    timestamp = models.TimeField(auto_now_add=True)
    section = models.ForeignKey(Section)
    user = models.ForeignKey(StarUser)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)

    class Meta:
        app_label='registrator'
