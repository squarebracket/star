from scheduler.models import Registration


class StudentService():

    COURSE_ALREADY_TAKEN_ERROR_MSG = "course already taken"
    NO_SECTION_AVAILABLE_ERROR_MSG = "no sections are open for this course"

    def RegisterStudentToCourse(self, student, course):

        already_taken_course_set = [e.course for e in student.studentrecord.studentrecordentry_set.all()]
        if course in already_taken_course_set:
            student.errorList.append(self.COURSE_ALREADY_TAKEN_ERROR_MSG)
        else:
            if len(course.section_set.all()) > 0:
                not_full_sections = [s for s in course.section_set.all() if s.isNotFull()]
                first_section = not_full_sections[0]

                registration = Registration(student=student, state="C", section=first_section)
                registration.save()
            else:
                student.errorList.append(self.NO_SECTION_AVAILABLE_ERROR_MSG)

        return student

