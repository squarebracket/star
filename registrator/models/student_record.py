from django.db import models
from user_stuff.models.student import Student


class StudentRecord(models.Model):
    student = models.OneToOneField(Student)
    standing = models.CharField(max_length=20)
    gpa = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)

    def __unicode__(self):
        return "student record for %s" % self.student.student_identifier

    class Meta:
        def __init__(self):
            pass

        app_label = 'registrator'