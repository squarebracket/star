from django.db import models
from uni_info.models import Course

class Requirement(models.Model):

    PREVIOUSLY_TAKEN = 1
    CONCURRENTLY_TAKEN = 2
    NUMBER_OF_CREDITS_COMPLETED = 3
    PASSED_EWT = 4

    REQUIREMENTS = (
        (PREVIOUSLY_TAKEN, "Prerequisite course"),
        (CONCURRENTLY_TAKEN, "Corequisite course"),
        (NUMBER_OF_CREDITS_COMPLETED, "Number of credits completed in degree"),
        (PASSED_EWT, "Passed the engineering writing test"),
    )

    type_help = "<br>".join(["/%s means %s" % (m[0], m[1]) for m in REQUIREMENTS])
    type = models.PositiveSmallIntegerField(choices=REQUIREMENTS, help_text=type_help)

    _value = models.PositiveSmallIntegerField(null=True, blank=True)
    _courses_that_satisfy = models.ManyToManyField(Course, null=True, blank=True, symmetrical=False, related_name='+')

    #FIXME: error handling here is pretty weak
    def set_satisfied_by(self, *args):
        self.save()
        for req in args:
            if type(req) is Course:
                self._courses_that_satisfy.add(req)
            else:
                self._value = req
        self.save()

    def get_or_create(self, *args):
        req_set = Requirement.objects.filter(type=self.type)
        for req in args:
            req_set = req_set.filter(_courses_that_satisfy=req)
        if len(req_set) == 0:
            self.set_satisfied_by(*args)
            return self
        elif len(req_set) == 1:
            return req_set[0]
        else:
            raise

    def __unicode__(self):
        if self._value is None and self._courses_that_satisfy.count() == 0:
            return 'empty requirement'
        elif self._value is not None:
            return "%s/%s" % (self._value, self.type)
        elif self._courses_that_satisfy.count == 1:
            return "%s - %s" % (self._courses_that_satisfy.all()[0], self.type)
        elif self._courses_that_satisfy.count > 1:
            return " or ".join(["%s %s" % (course.course_letters, course.course_numbers) for course in self._courses_that_satisfy.all()]) + '/%s' % self.type

    class Meta:
        app_label = 'uni_info'