from django.db import models
from scheduler.choices import STUDENT_TYPE_CHOICES
from scheduler.models.academic_program import AcademicProgram
from scheduler.models.schedule import CalculatedSchedule
from scheduler.models.star_user import StarUser
from scheduler.resources import Resource


class Student(StarUser):
    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    @property
    def registered_courses(self):
        return [section.course for section in self.registered_sections]

    @property
    def registered_sections(self):
        return [sre.section for sre in self.studentrecord.studentrecordentry_set.all() if sre.is_register_state]

    @property
    def completed_courses(self):
        return [sre.section.course for sre in self.studentrecord.studentrecordentry_set.all() if sre.is_complete_state]

    def create_schedule_from_registered_courses(self):
        schedule = CalculatedSchedule()
        for sec in self.registered_sections:
            schedule.add_section(sec)

        return schedule

    def drop_course(self, course):
        """
        Drops the student from a course
        """
        if course not in self.registered_courses:
            self.error_list.append(Resource.COURSE_NOT_REGISTERED_ERROR_MSG)
            return
        matching = [sre for sre in self.studentrecord.studentrecordentry_set.all()
                    if sre.section.course.name == course.name]
        for match in matching:
            match.delete()

    def add_to_schedule(self, schedule, course, semester):
        """
        Adds the course for a semester to a schedule        """
        from scheduler.models import StudentRecordEntry
        return

    def register_for_course(self, course, semester):
        """
        Registers the student to a course in a semester
        """
        from scheduler.models import StudentRecordEntry

        #Validate if course has already been taken
        if course in self.completed_courses:
            self.error_list.append(Resource.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return

        #Validate if course is already registered
        if course in self.registered_courses:
            self.error_list.append(Resource.COURSE_ALREADY_REGISTERED_ERROR_MSG)
            return

        #Validate if there is a section available for course
        if len(course.section_set.all()) == 0:
            self.error_list.append(Resource.NO_SECTION_AVAILABLE_ERROR_MSG)
            return

        #Validate if all pre-requisite has been met
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in self.completed_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.error_list.append(Resource.PRE_REQ_NOT_FULFILLED + missing_course.name)
                return

        #Validate if all co-requisite has been met
        if len(course.corequiste_list.all()) > 0:
            not_fulfilled = [coreq for coreq in course.corequiste_list.all()
                             if coreq not in self.registered_courses]
            if len(not_fulfilled) > 0:
                for missing_course in not_fulfilled:
                    self.error_list.append(Resource.CO_REQ_NOT_FULFILLED + missing_course.name)
                return

        #Validate if there is a section available in the requested semester
        sections_matching_semester = [s for s in course.section_set.all() if
                                      s.semester_year.name == semester.name]
        if len(sections_matching_semester) == 0:
            self.error_list.append(Resource.NO_SECTION_AVAILABLE_IN_SEMESTER)
            return

        #Validate if there is a section that is not full
        not_full_sections = [s for s in sections_matching_semester if
                             s.is_not_full()]
        if len(not_full_sections) == 0:
            self.error_list.append(Resource.ALL_SECTIONS_FULL_ERROR_MSG)
            return

        #Validate for conflict against existing registered sections
        registered_sections_for_semester = [sre.section for sre in self.studentrecord.studentrecordentry_set.all() if
                                            sre.is_register_state and sre.section.semester_year.name == semester.name]

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
            self.error_list.append(Resource.CONFLICT_FOUND_IN_SCHEDULE + " " + str(conflict_section))
            return

        #No errors, add into student record entry
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