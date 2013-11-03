from django.db import models


class Building(models.Model):
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    province = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=256)
    campus = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'