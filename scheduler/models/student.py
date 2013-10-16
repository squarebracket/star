from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.star_user import StarUser
from scheduler.resources import Resource


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

    def drop_course(self, course):
        if course not in self.registered_courses:
            self.errorList.append(Resource.COURSE_NOT_REGISTERED_ERROR_MSG)
            return
        matching = [sre for sre in self.studentrecord.studentrecordentry_set.all()
                    if sre.section.course.name == course.name]
        for match in matching:
            match.delete()

    def register_for_course(self, course, semester):
        from scheduler.models import StudentRecordEntry

        if course in self.completed_courses:
            self.errorList.append(Resource.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return
        if course in self.registered_courses:
            self.errorList.append(Resource.COURSE_ALREADY_REGISTERED_ERROR_MSG)
            return
        if len(course.section_set.all()) == 0:
            self.errorList.append(Resource.NO_SECTION_AVAILABLE_ERROR_MSG)
            return
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in self.completed_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.errorList.append(Resource.PRE_REQ_NOT_FULFILLED + missing_course.name)
                return
        if len(course.corequiste_list.all()) > 0:
            not_fulfilled = [coreq for coreq in course.corequiste_list.all()
                             if coreq not in self.registered_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.errorList.append(Resource.CO_REQ_NOT_FULFILLED + missing_course.name)
                return

        not_full_sections = [s for s in course.section_set.all() if
                             s.is_not_full() and s.semester_year.name == semester.name]
        if len(not_full_sections) == 0:
            self.errorList.append(Resource.ALL_SECTIONS_FULL_ERROR_MSG)
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