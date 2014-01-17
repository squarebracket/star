from django.db import models
from user_stuff.models.student import Student
from decimal import *


class StudentRecord(models.Model):
    student = models.OneToOneField(Student)
    # this should be a function maybe?
    _standing = models.CharField(max_length=20)
    # this should be a function maybe?
    _gpa = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)

    @property
    def standing(self):
        return self._standing

    @property
    def gpa(self):
        total_credits = 0
        total_grades = Decimal(0.00)
        for entry in self.studentrecordentry_set.all():
            if entry.result_grade is not None:
                total_credits += entry.section.course.course_credits
                total_grades += entry.result_grade * entry.section.course.course_credits
        print total_credits
        getcontext().prec=3
        return Decimal(total_grades / total_credits)


    def __unicode__(self):
        return "student record for %s" % self.student.student_identifier

    class Meta:
        def __init__(self):
            pass

        app_label = 'registrator'