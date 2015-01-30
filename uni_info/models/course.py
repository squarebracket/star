from django.db import models
from django.db.models import Q
from uni_info.models.department import Department

import re

NUMBER_OF_CREDITS_COMPLETED = 1


class CourseManager(models.Manager):

    def get(self, code=None, **kwargs):
        if code:
            m = re.match('([A-Z]{1,4}) ?(\d{1,3}[A-Z]?)', code, re.I)
            return self.model.objects.get(course_letters=m.group(1).upper(), course_numbers=int(m.group(2)))
        else:
            return super(CourseManager, self).get(**kwargs)


class Course(models.Model):

    OPEN_TO_ALL = 0
    PRIORITY_TO_SAME_FACULTY = 1
    ONLY_OPEN_TO_SAME_FACULTY = 2

    OPENNESS_CHOICES = (
        (OPEN_TO_ALL, "Open to all students"),
        (PRIORITY_TO_SAME_FACULTY, "Priority given to students whose program "
                                   "requires the course and to students in "
                                   "the same faculty as the course"),
        (ONLY_OPEN_TO_SAME_FACULTY, "Only open to students whose program"
                                    "requires the course and to students in "
                                    "the same faculty as the course"),
    )

    course_letters = models.CharField(max_length=4)
    course_numbers = models.CharField(max_length=5)
    department = models.ForeignKey(Department)
    openness = models.PositiveSmallIntegerField(
        help_text='Whether or not the course is open to all students, '
                  'priority is given to students in the program, or only '
                  'open to students enrolled in the program.', choices=
                  OPENNESS_CHOICES)
    name = models.CharField(max_length=40, verbose_name='Course title')
    description = models.CharField(max_length=256,
                                   help_text='Description as it appears in '
                                             'the academic calendar')
    course_credits = models.IntegerField(default=0.0)

    # for debug purposes, provide a string to store the scraped prerequisites
    _scraped_prerequisite_text = models.TextField(null=True, blank=True)
    requirements = models.ManyToManyField('Requirement', symmetrical=False, related_name='+')

    objects = CourseManager()

    def save_scraped_prerequisite_text(self, text):
        self._scraped_prerequisite_text = text
        self.save()

    def get_sections_for_semester(self, semester):
        """
        get sessions matching semester
        """
        sections_matching_semester = [s for s in self.section_set.filter(semester_year=semester)]
        return sections_matching_semester

    def get_section_tree_for_semester(self, semester):
        """
        Recursively populate a multi-level dict/list representing all the
        sections attached to this section
        """
        from uni_info.models import Section
        direct_descendants = [m._get_children() for m in self.section_set.filter(
            sec_type=Section.LECTURE, semester_year=semester)]
        try:
            if type(direct_descendants[0]) == type(dict()):
                d = {}
                # print direct_descendants
                for a in direct_descendants:
                    for (k, v) in a.iteritems():
                        d[k] = v
                return d
        except IndexError:
            pass
        if len(direct_descendants) == 0:
            return self
        else:
            return {self: direct_descendants}

    @property
    def section_perms(self):
        from scheduler.models.schedule_generator import get_section_permutations
        perms = get_section_permutations(self)
        return perms

    def leaf_sections_for_semesters(self, list_of_semesters):
        query = Q()
        for semester in list_of_semesters:
            query = query | Q(semester_year__id=semester)
        return self.section_set.filter(query, section=None)

    @staticmethod
    def full_search(text):
        results = []
        m = re.match('([A-Z]{1,4}) ?(\d{1,3}[A-Z]?)', text, re.I)
        if m:
            results = Course.objects.filter(
                Q(course_letters__icontains=m.group(1)) &
                Q(course_numbers__icontains=m.group(2))
            )
        else:
            results = Course.objects.filter(
                Q(course_letters__icontains=text.strip()) |
                Q(course_numbers__icontains=text.strip()) |
                Q(name__icontains=text.strip())
            )
        if len(results) > 0:
            return results
        else:
            raise Course.DoesNotExist

    @staticmethod
    def searcher(text):
        m = re.match('([A-Z]) ?(\d{3}[A-Z]?)', text, re.I)
        if m:
            try:
                course = Course.objects.get(course_letters=m.group(1),
                                            course_numbers=m.group(2))
                return course
            except Course.DoesNotExist as error:
                raise error

    @staticmethod
    def search_by_regex(course_name):
        """
        Search for course by regex
        """
        courses = []

        try:
            for course in Course.objects.filter(course_letters__regex=course_name):
                courses.append(course)

        except Course.DoesNotExist:
            return 'does not exist'

        return courses

    def __unicode__(self):
        return "%s %s" % (self.course_letters, self.course_numbers)

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'