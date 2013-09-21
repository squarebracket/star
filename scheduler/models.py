#This file contains all the Model in the application
from django.contrib.auth.models import User
from django.db import models
from scheduler.choices import DAY_OF_WEEK_CHOICES, PROGRAM_TYPE_CHOICES, GENDER_CHOICES, STUDENT_TYPE_CHOICES, SEMESTER_CHOICES, TIME_OF_DAY_CHOICES


class StarUser(User):
    date_of_birth = models.DateField('date of birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)


class AcademicProgram(models.Model):
    name = models.CharField(max_length=20)
    total_required_credits = models.IntegerField(default=0)
    required_gpa = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    type = models.CharField(max_length=1, choices=PROGRAM_TYPE_CHOICES)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=20)
    course_credits = models.IntegerField(default=0.0)
    academic_program = models.ForeignKey(AcademicProgram)
    prerequiste_list = models.ManyToManyField('self', through='Prerequisite', symmetrical=False, related_name="prerequsite_relation")
    corequiste_list = models.ManyToManyField('self', through='Corequisite', symmetrical=False, related_name="corequisite_reltion")

    def __unicode__(self):
        return self.name


class AcademicRequirement(models.Model):
    academic_program = models.ForeignKey(AcademicProgram)
    name = models.CharField(max_length=20)
    required_credits = models.IntegerField(default=0)
    allowable_courses = models.ManyToManyField(Course)

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    course = models.ForeignKey(Course)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)

    def __unicode__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(default=0)
    available_start_time = models.TimeField(name="available start time")
    available_end_time = models.TimeField(name="available end time")


class ScheduleItem(models.Model):
    location = models.ForeignKey(Facility)
    start_time = models.TimeField(name="start time")
    end_time = models.TimeField(name="end time")
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES)
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return self.location + " from " + self.start_time + " to " + self.end_time + " on " + self.day_of_week


class Student(StarUser):
    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    class Meta:
        verbose_name = "student"


class StudentRecord(models.Model):
    student = models.ForeignKey(Student)
    standing = models.CharField(max_length=20)
    gpa = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)


class StudentRecordEntry(models.Model):
    student_record = models.ForeignKey(StudentRecord)
    course = models.ForeignKey(Course)
    result_grade = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)


class Registration(models.Model):
    student = models.ForeignKey(Student)
    section = models.ForeignKey(Section)


class Professor(StarUser):
    faculty = models.CharField(max_length=20)

    class Meta:
        verbose_name = "professor"


class Registrar(StarUser):
    faculty = models.CharField(max_length=20)

    class Meta:
        verbose_name = "registrar"


class Director(StarUser):
    program = models.ForeignKey(AcademicProgram)

    class Meta:
        verbose_name = "director"


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_p")
    prerequisite_course = models.ForeignKey(Course, related_name="prerequisite_course")


class Corequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_c")
    corequisite_course = models.ForeignKey(Course, related_name="corequisite_course")


class Lab(ScheduleItem):
    name = models.CharField(max_length=20)
    technician = models.ForeignKey(Student)


class Tutorial(ScheduleItem):
    name = models.CharField(max_length=20)
    tutor = models.ForeignKey(Student)


class Lecture(ScheduleItem):
    professor = models.ForeignKey(Professor)


class ScheduleConstraintSet(models.Model):
    name = models.CharField(max_length=20)
    student = models.ForeignKey(Student)


class ScheduleConstraint(models.Model):
    constraint_set = models.ForeignKey(ScheduleConstraintSet)
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES)
    time_of_day = models.CharField(max_length=1, choices=TIME_OF_DAY_CHOICES)
    course_name = models.CharField(max_length=20)


class CalculatedSchedule(models.Model):
    constraint_set = models.OneToOneField(ScheduleConstraintSet)
    items = models.ManyToManyField(ScheduleItem)


