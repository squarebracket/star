class StudentService():

    def RegisterStudentToCourse(self, student, course):

        courseSet = [e.course for e in student.studentrecord.studentrecordentry_set]
        if course in courseSet:
            student.errorList.add("course already taken")

        return student

