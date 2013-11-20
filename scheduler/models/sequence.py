from django.db import models
from uni_info.models import Course, Semester
from user_stuff.models import StarUser
from scheduler.models import ScheduleGenerator, SemesterSchedule

class SemesterSequence(models.Model):
    courses_rel = models.ManyToManyField(Course, symmetrical=False, related_name='semseq+')
    semester = models.ForeignKey(Semester)
    seq = models.ForeignKey('Sequence')
    sem_sched = models.ForeignKey(SemesterSchedule, null=True)

    def add_course(self, course):
        self.save()
        self.courses_rel.add(course)
        self.save()

    def add_courses(self, *args):
        if type(args[0]) is list:
            courses = args[0]
        else:
            courses = args
        if type(courses) is list or tuple:
            for course in courses:
                self.add_course(course)
        else:
            self.add_course(courses)

    def remove_course(self, course):
        self.save()
        self.courses_rel.remove(course)
        self.save()

    def remove_courses(self, courses):
        if type(courses) is list:
            for course in courses:
                self.remove_course(course)
        else:
            self.remove_course(courses)

    def get_possible_schedules(self):
        gen_r = ScheduleGenerator(
            list_of_courses=self.courses_rel.all(),
            semester=self.semester
        )
        return gen_r.generate_schedules()

    def implemented_by(self, semsched):
        self.sem_sched = semsched

    @property
    def courses(self):
        return list(self.courses_rel.all())

    def __unicode__(self):
        return str(self.semester)

    class Meta:
        app_label = 'scheduler'


class Sequence(models.Model):
    user = models.ForeignKey(StarUser, null=True)

    class Meta:
        app_label = 'scheduler'