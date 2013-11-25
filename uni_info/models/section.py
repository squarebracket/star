from django.db import models
from uni_info.models.facility import Facility
from uni_info.models.course import Course
from uni_info.models.semester import Semester
from itertools import chain

from user_stuff.models import StarUser


class Section(models.Model):
    """
    Describes a Section
    """

    LECTURE = 1
    TUTORIAL = 2
    LAB = 3
    SEMINAR = 4
    ONLINE = 5
    UNSCHEDULED = 6
    WORKSHOP = 7
    CONFERENCE = 8
    STUDIO = 9
    FWORK = 10

    SECTION_TYPES = (
        (LECTURE, 'Lecture'),
        (TUTORIAL, 'Tutorial'),
        (LAB, 'Lab'),
        (UNSCHEDULED, 'Unscheduled'),
        (ONLINE, 'Online'),
        (SEMINAR, 'Seminar'),
        (WORKSHOP, 'Workshop'),
        (CONFERENCE, 'Conference'),
        (STUDIO, 'Studio'),
        (FWORK, 'Field Work'),
    )

    course = models.ForeignKey(Course)

    name = models.CharField(max_length=20)
    capacity = models.IntegerField(default=0)
    semester_year = models.ForeignKey(Semester, null=True)
    sec_type = models.PositiveSmallIntegerField(max_length=1, verbose_name="Section Type")
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    days = models.CharField(max_length=7)
    location = models.ForeignKey(Facility, null=True)
    _instructor = models.ForeignKey(StarUser, null=True)
    instructor_text = models.CharField(max_length=256, null=True, blank=True)
    week = models.PositiveSmallIntegerField(null=True, blank=True)

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

    @property
    def section_tree_from_here(self):
        result_list = self._get_children()
        return result_list

    def _get_children(self):
        """
        Recursively populate a multi-level dict/list representing all the
        sections attached to this section
        """
        direct_descendants = [m._get_children() for m in self.section_set.all()]
        try:
            if type(direct_descendants[0]) == type(dict()):
                d = {}
                for a in direct_descendants:
                    for (k, v) in a.iteritems():
                        d[k] = v
                return {self: d}
        except IndexError:
            pass
        if len(direct_descendants) == 0:
            return self
        else:
            return {self: direct_descendants}

    def _has_children(self):
        return self.section_set.count()

    def __unicode__(self):
        return "%s%s: %s %s/%s" % (self.course.course_letters,
            self.course.course_numbers, self.sec_type, self.name, self.semester_year)

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'
