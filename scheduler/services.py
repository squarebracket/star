from scheduler.models import Registration


class RegistrationService():

    def __init__(self):
        pass

    PRE_REQ_NOT_FULFILLED = "pre-req not fulfilled: "
    COURSE_ALREADY_TAKEN_ERROR_MSG = "course already taken"
    NO_SECTION_AVAILABLE_ERROR_MSG = "no sections are open for this course"

    def createRegistrationFor(self, student, course):

        already_taken_course_set = [e.course for e in student.studentrecord.studentrecordentry_set.all()]
        if course in already_taken_course_set:
            student.errorList.append(self.COURSE_ALREADY_TAKEN_ERROR_MSG)
            return student
        if len(course.section_set.all()) == 0:
            student.errorList.append(self.NO_SECTION_AVAILABLE_ERROR_MSG)
            return student
        if len(course.prerequiste_list.all()) > 0:
            not_fulfilled = [prereq for prereq in course.prerequiste_list.all()
                             if prereq not in already_taken_course_set]
            if len(not_fulfilled) > 0:
                # this looks ugly -- better way to do it?
                student.errorList.append(self.PRE_REQ_NOT_FULFILLED +
                                         str([str(c.name) for c in not_fulfilled]).strip("[]"))
                return student

        not_full_sections = [s for s in course.section_set.all() if s.is_not_full()]
        first_section = not_full_sections[0]

        registration = Registration(student=student, state="C", section=first_section)
        registration.save()

        return student

