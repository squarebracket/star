#This file contains all the Models for the application
from datetime import time

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from scheduler.choices import *


class StarUser(AbstractUser):
    date_of_birth = models.DateField('date of birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    errorList = []

    custom_objects = UserManager()

    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['date_of_birth']

    class Meta:
        app_label = 'auth'


class AcademicInstitution(models.Model):
    name = models.CharField(max_length=256)
    established_on = models.DateField("established on")

    def __unicode__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=256)
    university = models.ForeignKey(AcademicInstitution)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=256)
    university = models.ForeignKey(AcademicInstitution)
    faculty = models.ForeignKey(Faculty)

    def __unicode__(self):
        return self.name


class AcademicProgram(models.Model):
    name = models.CharField(max_length=256)
    faculty = models.ForeignKey(Faculty)
    total_required_credits = models.IntegerField(default=0)
    required_gpa = models.DecimalField(default=0.00, decimal_places=2,
                                       max_digits=10)
    type = models.CharField(max_length=1, choices=PROGRAM_TYPE_CHOICES)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    course_letters = models.CharField(max_length=4)
    course_numbers = models.CharField(max_length=5)
    department = models.ForeignKey(Department)
    openness = models.PositiveSmallIntegerField(
        help_text='Whether or not the course is open to all students, '
                  'priority is given to students in the program, or only '
                  'open to students enrolled in the program.')
    name = models.CharField(max_length=20, verbose_name='Course title')
    description = models.CharField(max_length=256,
                                   help_text='Description as it appears in '
                                             'the academic calendar')
    course_credits = models.IntegerField(default=0.0)
    prerequiste_list = models.ManyToManyField('self',
                                              through='Prerequisite',
                                              symmetrical=False,
                                              related_name="prerequsite_relation")
    corequiste_list = models.ManyToManyField('self',
                                             through='Corequisite',
                                             symmetrical=False,
                                             related_name="corequisite_reltion")

    def __unicode__(self):
        return "%s %s" % (self.course_letters, self.course_numbers)


class AcademicRequirement(models.Model):
    academic_program = models.ForeignKey(AcademicProgram)
    name = models.CharField(max_length=256)
    required_credits = models.IntegerField(default=0)
    allowable_courses = models.ManyToManyField(Course)

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    course = models.ForeignKey(Course)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)

    def is_not_full(self):
        return len(self.registration_set.all()) < self.capacity

    def __unicode__(self):
        return str(self.course.name) + " " + str(self.name)


class Building(models.Model):
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    province = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=20, unique=True)
    building = models.ForeignKey(Building)
    capacity = models.IntegerField(default=0)
    available_start_time = models.TimeField('available start time',
                                            default=time(hour=8, minute=0))
    available_end_time = models.TimeField('available end time',
                                          default=time(hour=22, minute=0))

    def __unicode__(self):
        return self.name


class ScheduleItem(models.Model):
    location = models.ForeignKey(Facility)
    start_time = models.TimeField('start time')
    end_time = models.TimeField('end time')
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES)
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return "%s from %s to %s on %s" % (self.location, self.start_time,
                                           self.end_time, self.day_of_week)


class Student(StarUser):
    program = models.ForeignKey(AcademicProgram)
    student_identifier = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=STUDENT_TYPE_CHOICES)

    def __unicode__(self):
        return "id#%s (%s %s)" % (self.student_identifier, self.first_name,
                                  self.last_name)

    class Meta:
        verbose_name = "student"


class StudentRecord(models.Model):
    student = models.OneToOneField(Student)
    standing = models.CharField(max_length=20)
    gpa = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)

    def __unicode__(self):
        return "student record for %s" % self.student.student_identifier


class StudentRecordEntry(models.Model):
    student_record = models.ForeignKey(StudentRecord)
    section = models.ForeignKey(Section, null=True)
    course = models.ForeignKey(Course, null=True)
    result_grade = models.DecimalField(default=0.00, decimal_places=2,
                                       max_digits=10)

    def __unicode__(self):
        return "id:%s, section:%s, grade:%s" % (self.student_record.student.student_identifier,
                                                str(self.section),
                                                self.result_grade)


class Registration(models.Model):
    student = models.ForeignKey(Student)
    section = models.ForeignKey(Section)
    state = models.CharField(max_length=1, choices=REGISTRATION_STATE_CHOICES)


class Professor(StarUser):
    faculty = models.ForeignKey(Faculty)

    class Meta:
        verbose_name = "professor"


class Registrar(StarUser):
    faculty = models.ForeignKey(Faculty)

    class Meta:
        verbose_name = "registrar"


class Director(StarUser):
    program = models.ForeignKey(AcademicProgram)

    class Meta:
        verbose_name = "director"


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_p")
    prerequisite_course = models.ForeignKey(Course,
                                            related_name="prerequisite_course")


class Corequisite(models.Model):
    course = models.ForeignKey(Course, related_name="course_c")
    corequisite_course = models.ForeignKey(Course,
                                           related_name="corequisite_course")


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


