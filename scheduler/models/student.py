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
            self.error_list.append(Resource.COURSE_NOT_REGISTERED_ERROR_MSG)
            return
        matching = [sre for sre in self.studentrecord.studentrecordentry_set.all()
                    if sre.section.course.name == course.name]
        for match in matching:
            match.delete()

    def register_for_course(self, course, semester):
        from scheduler.models import StudentRecordEntry

        if course in self.completed_courses:
            self.error_list.append(Resource.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return
        if course in self.registered_courses:
            self.error_list.append(Resource.COURSE_ALREADY_REGISTERED_ERROR_MSG)
            return
        if len(course.section_set.all()) == 0:
            self.error_list.append(Resource.NO_SECTION_AVAILABLE_ERROR_MSG)
            return
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in self.completed_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.error_list.append(Resource.PRE_REQ_NOT_FULFILLED + missing_course.name)
                return
        if len(course.corequiste_list.all()) > 0:
            not_fulfilled = [coreq for coreq in course.corequiste_list.all()
                             if coreq not in self.registered_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.error_list.append(Resource.CO_REQ_NOT_FULFILLED + missing_course.name)
                return

        sections_matching_semester = [s for s in course.section_set.all() if
                                      s.semester_year.name == semester.name]
        if len(sections_matching_semester) == 0:
            self.error_list.append(Resource.NO_SECTION_AVAILABLE_IN_SEMESTER)
            return

        not_full_sections = [s for s in sections_matching_semester if
                             s.is_not_full()]
        if len(not_full_sections) == 0:
            self.error_list.append(Resource.ALL_SECTIONS_FULL_ERROR_MSG)
            return

        registered_sections_for_semester = [sre.section for sre in self.studentrecord.studentrecordentry_set.all() if
                                            sre.state == "R" and sre.section.semester_year.name == semester.name]

        to_register_section = None
        conflict_section = None
        if len(registered_sections_for_semester) == 0:
            to_register_section = not_full_sections[0]
        else:
            for check_section in not_full_sections:
                conflict_section = None
                for registered_section in registered_sections_for_semester:
                    if registered_section.conflicts_with(check_section):
                        conflict_section = registered_section

                if conflict_section is None:
                    to_register_section = check_section

        if to_register_section is None and conflict_section is not None:
            self.error_list.append(Resource.CONFLICT_FOUND_IN_SCHEDULE + conflict_section)
            return

        reg_student_record_entry = StudentRecordEntry(student_record=self.studentrecord,
                                                      state="R", section=to_register_section)
        reg_student_record_entry.save()
        self.info_list.append(Resource.REGISTERED_SUCCESS_MSG)
        return

    def __unicode__(self):
        return "id#%s (%s %s)" % (self.student_identifier, self.first_name,
                                  self.last_name)

    class Meta:
        def __init__(self):
            pass

        verbose_name = "student"
        app_label = 'scheduler'