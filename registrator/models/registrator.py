from django.db import models

class Registrator(models.Model):
    timestamp = models.TimeField(auto_now_add=True)

