from django.db import models
from uni_info.models import Course


class Requirement(models.Model):
    NUMBER_OF_CREDITS_COMPLETED = 1


    REQUIREMENTS = (
        (NUMBER_OF_CREDITS_COMPLETED, "Number of credits completed in degree"),
    )
    type = models.PositiveSmallIntegerField(choices=REQUIREMENTS)
    value = models.PositiveSmallIntegerField(null=True)
    course = models.ForeignKey(Course)

    class Meta:
        app_label = 'uni_info'