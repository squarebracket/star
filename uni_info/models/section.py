from django.db import models
from uni_info.models.course import Course
from uni_info.models.semester import Semester
from itertools import chain

from user_stuff.models import StarUser


class Section(models.Model):

    LECTURE = 1
    TUTORIAL = 2
    LAB = 3
    SEMINAR = 4
    ONLINE = 5
    UNSCHEDULED = 6

    SECTION_TYPES = (
        (LECTURE, 'Lecture'),
        (TUTORIAL, 'Tutorial'),
        (LAB, 'Lab'),
        (UNSCHEDULED, 'Unscheduled'),
        (ONLINE, 'Online'),
        (SEMINAR, 'Seminar'),
    )

    course = models.ForeignKey(Course)

    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    semester_year = models.ForeignKey(Semester, null=True)
    sec_type = models.PositiveSmallIntegerField(max_length=1, verbose_name="Section Type")
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    days = models.CharField(max_length=7)
    _instructor = models.ForeignKey(StarUser, null=True)

    cancelled = models.BooleanField(default=False)

    parent_section = models.ForeignKey('self', null=True)

    _scraped_as_full = models.BooleanField(default=False)

    @property
    def is_not_full(self):
        # if capacity is 0, it means we don't have the capacity information
        if self.capacity == 0:
            # so we have to rely on scraped data
            return self._scraped_as_full
        # otherwise, we can trust the data
        else:
            # so check if we've actually hit capacity
            return len(self.studentrecordentry_set.all()) < self.capacity

    def conflicts_with(self, section):

        for my_item in self.all_schedule_items:
            for test_item in section.all_schedule_items:
                if my_item.conflicts_with(test_item):
                    return True
        return False

    @property
    def child_sections(self):
        result_list = self._get_children()
        return result_list

    def _get_children(self):
        direct_descendants = [m._get_children() for m in self.section_set.all()]
        if len(direct_descendants) == 0:
            return self
        else:
            return {self: direct_descendants}
    #@property
    #def lectures(self):
    #    from uni_info.models import Lecture
    #    return Lecture.objects.filter(section=self)
    #
    #@property
    #def labs(self):
    #    from uni_info.models import Lab
    #    return Lab.objects.filter(section=self)
    #
    #@property
    #def tutorials(self):
    #    from uni_info.models import Tutorial
    #    return Tutorial.objects.filter(section=self)

    def __unicode__(self):
        return str(self.course.name) + " " + str(self.name) + " " + str(self.semester_year)

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'