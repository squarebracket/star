from django.db import models
from scheduler.choices import REGISTRATION_STATE_CHOICES
from scheduler.models.section import Section
from scheduler.models.student_record import StudentRecord


class StudentRecordEntry(models.Model):
    student_record = models.ForeignKey(StudentRecord)
    section = models.ForeignKey(Section, null=True)
    state = models.CharField(max_length=1, choices=REGISTRATION_STATE_CHOICES)
    result_grade = models.DecimalField(default=0.00, decimal_places=2,
                                       max_digits=10)

    def __unicode__(self):
        return "id:%s, section:%s, grade:%s" % (self.student_record.student.student_identifier,
                                                str(self.section),
                                                self.result_grade)

    @property
    def is_register_state(self):
        return self.state == "R"

    @property
    def is_complete_state(self):
        return self.state == "C"

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'