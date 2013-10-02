from datetime import date, time
import logging

from django.test import TestCase

from scheduler.models import Student, AcademicProgram, Course, \
    AcademicRequirement, StudentRecord, StudentRecordEntry, Prerequisite, \
    Section, Lecture, Professor, Registration, Building, Facility, \
    AcademicInstitution, Faculty, Department, Semester


class SimpleModelsTest(TestCase):

    def test_adding_a_student(self):
        concordia = AcademicInstitution(name="Concordia University",
                                        established_on=date(year=1974, month=8, day=24))
        concordia.save()
        logging.debug(AcademicInstitution.objects.all())
        encs = Faculty(name="Faculty of Engineering and Computer Science",
                       description="xx", university=concordia)
        encs.save()
        business = Faculty(name="Faculty of Business", description="xx",
                           university=concordia)
        business.save()

        #Make test department
        cse = Department(name="Computer Science and Software Engineering",
                         university=concordia, faculty=encs)
        cse.save()

        #Setup the Program for the student
        soen_program = AcademicProgram(name="soen", faculty=encs,
                                       required_gpa=2.8, type="U")

        # test Soen program, contains core courses
        soen_program.save()

        soen101 = Course(course_letters="SOEN", course_numbers="101",
                         name="Some Soen Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        soen102 = Course(course_letters="SOEN", course_numbers="102",
                         name="Some Soen Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        soen201 = Course(course_letters="SOEN", course_numbers="201",
                         name="Some Soen Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        soen202 = Course(course_letters="SOEN", course_numbers="202",
                         name="Some Soen Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        soen301 = Course(course_letters="SOEN", course_numbers="301",
                         name="Some Soen Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")

        soen101.save()
        soen102.save()
        soen201.save()
        soen202.save()
        soen301.save()

        #Setup course prerequisites
        soen201_prereq101 = Prerequisite(course=soen201, prerequisite_course=soen101)
        soen202_prereq102 = Prerequisite(course=soen202, prerequisite_course=soen102)
        soen301_prereq201 = Prerequisite(course=soen301, prerequisite_course=soen201)
        soen301_prereq202 = Prerequisite(course=soen301, prerequisite_course=soen202)

        soen201_prereq101.save()
        soen202_prereq102.save()
        soen301_prereq201.save()
        soen301_prereq202.save()

        # test Elective program, contains elective courses
        elec_program = AcademicProgram(name="elec", faculty=business)
        elec_program.save()

        elec101 = Course(course_letters="ELEC", course_numbers="101",
                         name="Some Elective Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        elec102 = Course(course_letters="ELEC", course_numbers="102",
                         name="Some Elective Course", openness=1, course_credits=4,
                         department=cse, description="Some course description")
        elec101.save()
        elec102.save()

        #Setup program requirements
        core_reqs = AcademicRequirement(name="Core", required_credits=12,
                                        academic_program=soen_program)
        elec_reqs = AcademicRequirement(name="Electives",
                                        required_credits=4,
                                        academic_program=soen_program)

        core_reqs.save()
        core_reqs.allowable_courses.add(soen101)
        core_reqs.allowable_courses.add(soen101)
        core_reqs.allowable_courses.add(soen201)
        core_reqs.allowable_courses.add(soen202)
        core_reqs.allowable_courses.add(soen301)
        core_reqs.save()

        elec_reqs.save()
        elec_reqs.allowable_courses.add(elec101)
        elec_reqs.allowable_courses.add(elec102)
        elec_reqs.save()

        #Setup Professor
        logging.info("Setup professor")
        prof_fancott = Professor(faculty=encs, date_of_birth=date(1950, 1, 1),
                                 gender="M")
        prof_fancott.save()

        semester = Semester(year=2000, period="F")

        #Setup Offerings by section
        section1_for_soen201 = Section(name="S1", capacity=20, course=soen201,
                                       semester_year=semester)
        section1_for_soen201.save()
        section2_for_soen201 = Section(name="S2", capacity=20, course=soen201,
                                       semester_year=semester)
        section2_for_soen201.save()

        hall_building = Building(name="Hall", address="123 Street",
                                 city="Montreal", province="Quebec",
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
                                                   day_of_week="Fri",
                                                   section=section1_for_soen201,
                                                   professor=prof_fancott)
        fri_lecture_for_soen201_section1.save()

        section1_for_soen202 = Section(name="S1", capacity=20, course=soen202,
                                       semester_year=semester)
        section1_for_soen202.save()
        section1_for_soen101 = Section(name="S1", capacity=20, course=soen101,
                                       semester_year=semester)
        section1_for_soen101.save()
        section1_for_elec101 = Section(name="S1", capacity=20, course=elec101,
                                       semester_year=semester)
        section1_for_elec101.save()

        student = Student(username="test_user", password="password",
                          first_name="test", last_name="user",
                          date_of_birth=date(1980, 1, 1),
                          gender='M')
        student.program = soen_program
        student.save()

        all_students = Student.objects.all()

        test_record = StudentRecord(student=student, standing="good", gpa=0.00)
        test_record.save()

        # The student has taken 2 courses already
        soen101_entry = StudentRecordEntry(student_record=test_record,
                                           section=section1_for_soen101, result_grade=3.8)
        elec101_entry = StudentRecordEntry(student_record=test_record,
                                           section=section1_for_elec101, result_grade=3.5)

        soen101_entry.save()
        elec101_entry.save()

        soen201_reg = Registration(student=student,
                                   section=section1_for_soen201)
        soen201_reg.save()

