from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser


class Student(StarUser):
    PRE_REQ_NOT_FULFILLED = "pre-req not fulfilled: "
    CO_REQ_NOT_FULFILLED = "co-req not fulfilled: "
    COURSE_ALREADY_TAKEN_ERROR_MSG = "course already taken"
    COURSE_ALREADY_REGISTERED_ERROR_MSG = "course already registered"
    NO_SECTION_AVAILABLE_ERROR_MSG = "no sections are open for this course"
    ALL_SECTIONS_FULL_ERROR_MSG = "all sections are full for this course"

    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    @property
    def registered_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "R"]

    @property
    def completed_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.state == "C"]

    def drop_course(self, course):
        pass

    def register_for_course(self, course):
        from scheduler.models import StudentRecordEntry

        if course in self.completed_courses:
            self.errorList.append(self.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return
        if course in self.registered_courses:
            self.errorList.append(self.COURSE_ALREADY_REGISTERED_ERROR_MSG)
            return
        if len(course.section_set.all()) == 0:
            self.errorList.append(self.NO_SECTION_AVAILABLE_ERROR_MSG)
            return
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in self.completed_courses]
            if len(not_fulfilled) > 0:
                # this looks ugly -- better way to do it?
                self.errorList.append(self.PRE_REQ_NOT_FULFILLED +
                                      str([str(c.name) for c in not_fulfilled]).strip("[]"))
                return
        if len(course.corequiste_list.all()) > 0:
            not_fulfilled = [coreq for coreq in course.corequiste_list.all()
                             if coreq not in self.registered_courses]
            if len(not_fulfilled) > 0:
                # this looks ugly -- better way to do it?
                self.errorList.append(self.CO_REQ_NOT_FULFILLED +
                                      str([str(c.name) for c in not_fulfilled]).strip("[]"))
                return

        not_full_sections = [s for s in course.section_set.all() if s.is_not_full()]
        if len(not_full_sections) == 0:
            self.errorList.append(self.ALL_SECTIONS_FULL_ERROR_MSG)
            return

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