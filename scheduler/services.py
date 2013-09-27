from scheduler.models import Registration


class StudentService():

    def RegisterStudentToCourse(self, student, course):

        courseSet = [e.course for e in student.studentrecord.studentrecordentry_set.all()]
        if course in courseSet:
            student.errorList.append("course already taken")
        else:
            if len(course.section_set.all()) > 0:
                first_section = course.section_set.all()[0]

                registration = Registration(student=student, state="C", section=first_section)
                registration.save()
            else:
                student.errorList.append("no sections are open for this course")

        return student

