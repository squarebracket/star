from datetime import date, time

from django.test import TestCase
from scheduler.models import Student, AcademicProgram, Course, AcademicRequirement, StudentRecord, StudentRecordEntry, Prerequisite, Section, Lecture, Professor, Registration, Building, Facility, AcademicInstitution, Faculty
from scheduler.services import StudentService


class SimpleModelsTest(TestCase):

    def test_adding_a_student(self):
        concordia = AcademicInstitution(name="Concordia University", established_on=date(year=1974, month=8, day=24))
        concordia.save()
        encs = Faculty(name="Faculty of Engineering and Computer Science", description="xx", university=concordia)
        encs.save()
        business = Faculty(name="Faculty of Business", description="xx", university=concordia)
        business.save()

        #Setup the Program for the student
        soenProgram = AcademicProgram(name="soen", faculty=encs, required_gpa=2.8, type="U")

                                      # test Soen program, contains core courses
        soenProgram.save()

        soen101 = Course(name="soen101", course_credits=4, faculty=encs)
        soen102 = Course(name="soen102", course_credits=4, faculty=encs)
        soen201 = Course(name="soen201", course_credits=4, faculty=encs)
        soen202 = Course(name="soen202", course_credits=4, faculty=encs)
        soen301 = Course(name="soen301", course_credits=4, faculty=encs)

        soen101.save()
        soen102.save()
        soen201.save()
        soen202.save()
        soen301.save()

        #Setup course prerequisites
        soen201Prereq101 = Prerequisite(course=soen201, prerequisite_course=soen101)
        soen202Prereq102 = Prerequisite(course=soen202, prerequisite_course=soen102)
        soen301Prereq201 = Prerequisite(course=soen301, prerequisite_course=soen201)
        soen301Prereq202 = Prerequisite(course=soen301, prerequisite_course=soen202)

        soen201Prereq101.save()
        soen202Prereq102.save()
        soen301Prereq201.save()
        soen301Prereq202.save()

        elecProgram = AcademicProgram(name="elec", faculty=business)  # test Elective program, contains elective courses
        elecProgram.save()

        elec101 = Course(name="elec101", course_credits=4, faculty=encs)
        elec102 = Course(name="elec102", course_credits=4, faculty=encs)
        elec101.save()
        elec102.save()

        #Setup program requirements
        coreRequirements = AcademicRequirement(name="Core", required_credits=12, academic_program=soenProgram)
        electiveRequirements = AcademicRequirement(name="Electives", required_credits=4, academic_program=soenProgram)

        coreRequirements.save()
        coreRequirements.allowable_courses.add(soen101)
        coreRequirements.allowable_courses.add(soen101)
        coreRequirements.allowable_courses.add(soen201)
        coreRequirements.allowable_courses.add(soen202)
        coreRequirements.allowable_courses.add(soen301)
        coreRequirements.save()

        electiveRequirements.save()
        electiveRequirements.allowable_courses.add(elec101)
        electiveRequirements.allowable_courses.add(elec102)
        electiveRequirements.save()

        print("setup professor")

        #Setup Professor
        prof_fancott = Professor(faculty=encs, date_of_birth=date(1950, 1, 1), gender="M")
        prof_fancott.save()

        #Setup Offerings by section
        section1_for_soen201 = Section(name="S1", capacity=20, course=soen201, semester="F")
        section1_for_soen201.save()
        section2_for_soen201 = Section(name="S2", capacity=20, course=soen201, semester="F")
        section2_for_soen201.save()

        hall_building = Building(name="Hall", address="123 Street", city="Montreal", province="Quebec",
                                 country="Canada", postal_code="x2c3v4")
        hall_building.save()

        room_h629 = Facility(name="H629", building=hall_building, capacity=50)
        room_h629.save()


        wed_lecture_for_soen201_section1 = Lecture(location=room_h629,
                                                   start_time=time(hour=10, minute=15, second=0),
                                                   end_time=time(hour=11, minute=30, second=0),
                                                   day_of_week="Wed",
                                                   section=section1_for_soen201,
                                                   professor=prof_fancott)

        wed_lecture_for_soen201_section1.save()
        fri_lecture_for_soen201_section1 = Lecture(location=room_h629,
                                                   start_time=time(hour=10, minute=15),
                                                   end_time=time(hour=11, minute=30),
                                                   day_of_week="Fri", section=section1_for_soen201,
                                                   professor=prof_fancott)
        fri_lecture_for_soen201_section1.save()

        section1_for_soen202 = Section(name="S1", capacity=20, course=soen202, semester="F")
        section1_for_soen202.save()

        student = Student(username="test_user", password="password", first_name="test", last_name="user",
                          date_of_birth=date(1980, 1, 1), gender='M')
        student.program = soenProgram
        student.save()

        allStudents = Student.objects.all()
        self.assertEqual(1, allStudents.count())

        studentRecord = StudentRecord(student=student, standing="good", gpa=0.00)
        studentRecord.save()

        # The student has taken 2 courses already
        soen101Entry = StudentRecordEntry(student_record=studentRecord, course=soen101, result_grade=3.8)
        elec101Entry = StudentRecordEntry(student_record=studentRecord, course=elec101, result_grade=3.5)

        soen101Entry.save()
        elec101Entry.save()

        soen201_reg = Registration(student=student, section=section1_for_soen201)
        soen201_reg.save()

