from django.db import models
from uni_info.models.department import Department

NUMBER_OF_CREDITS_COMPLETED = 1


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

    @staticmethod
    def search_by_regex(course_name):
        """
        Search for course by regex
        """
        courses = []

        try:
            for course in Course.objects.filter(name__regex=course_name):
                courses.append(course)

        except Course.DoesNotExist:
            print('does not exist')

        return courses

    def __unicode__(self):
        return "%s %s" % (self.course_letters, self.course_numbers)

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'