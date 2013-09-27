from scheduler.models import Registration


class StudentService():

    COURSE_ALREADY_TAKEN_ERROR_MSG = "course already taken"
    NO_SECTION_AVAILABLE_ERROR_MSG = "no sections are open for this course"

    def RegisterStudentToCourse(self, student, course):

        courseSet = [e.course for e in student.studentrecord.studentrecordentry_set.all()]
        if course in courseSet:
            student.errorList.append(self.COURSE_ALREADY_TAKEN_ERROR_MSG)
        else:
            if len(course.section_set.all()) > 0:
                first_section = course.section_set.all()[0]

                registration = Registration(student=student, state="C", section=first_section)
                registration.save()
            else:
                student.errorList.append(self.NO_SECTION_AVAILABLE_ERROR_MSG)

        return student

