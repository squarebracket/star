from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser
from scheduler.models import StudentRecordEntry


class Student(StarUser):

    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    @property
    def registered_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "R"]

    @property
    def completed_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "C"]

    def register_for_course(self, course):
        not_full_sections = [s for s in course.section_set.all() if s.is_not_full()]
        first_section = not_full_sections[0]
        reg_student_record_entry = StudentRecordEntry(student_record=self.studentrecord,
                                                      state="R", section=first_section)
        reg_student_record_entry.save()


    def __unicode__(self):
        return "id#%s (%s %s)" % (self.student_identifier, self.first_name,
                                  self.last_name)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "student"
        app_label = 'scheduler'