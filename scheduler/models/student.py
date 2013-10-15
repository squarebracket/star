from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser


class Student(StarUser):
    PRE_REQ_NOT_FULFILLED = "pre-req not fulfilled: "
    COURSE_ALREADY_TAKEN_ERROR_MSG = "course already taken"
    NO_SECTION_AVAILABLE_ERROR_MSG = "no sections are open for this course"

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
        from scheduler.models import StudentRecordEntry
        already_taken_course_set = [e.section.course for e in self.studentrecord.studentrecordentry_set.all()]
        if course in already_taken_course_set:
            self.errorList.append(self.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return
        if len(course.section_set.all()) == 0:
            self.errorList.append(self.NO_SECTION_AVAILABLE_ERROR_MSG)
            return
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in already_taken_course_set]
            if len(not_fulfilled) > 0:
                # this looks ugly -- better way to do it?
                self.errorList.append(self.PRE_REQ_NOT_FULFILLED +
                                         str([str(c.name) for c in not_fulfilled]).strip("[]"))
                return

        not_full_sections = [s for s in course.section_set.all() if s.is_not_full()]
        first_section = not_full_sections[0]

        reg_student_record_entry = StudentRecordEntry(student_record=self.studentrecord,
                                                      state="R", section=first_section)
        reg_student_record_entry.save()
        return

    def __unicode__(self):
        return "id#%s (%s %s)" % (self.student_identifier, self.first_name,
                                  self.last_name)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "student"
        app_label = 'scheduler'