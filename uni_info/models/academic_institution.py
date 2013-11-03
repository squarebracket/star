from django.db import models


class AcademicInstitution(models.Model):
    name = models.CharField(max_length=256)
    established_on = models.DateField("established on")

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'