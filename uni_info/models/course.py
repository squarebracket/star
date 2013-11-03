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
    name = models.CharField(max_length=20, verbose_name='Course title')
    description = models.CharField(max_length=256,
                                   help_text='Description as it appears in '
                                             'the academic calendar')
    course_credits = models.IntegerField(default=0.0)
    prerequisite_courses = models.ManyToManyField('self', symmetrical=False,
                                           related_name="pre+")
    corequisite_courses = models.ManyToManyField('self', symmetrical=False,
                                          related_name="co+")
    # this will be used until a better implementation exists for storing
    # other kinds of requirements
    other_requirements = models.TextField(verbose_name=
                                          "Other prerequisite information",
                                          null=True, blank=True)
    # for debug purposes, provide a string to store the scraped prerequisites
    _scraped_prerequisite_text = models.TextField(null=True, blank=True)

    def get_sessions_matching_semester(self, semester):
        """
        get sessions matching semester
        """
        sections_matching_semester = [s for s in self.section_set.all() if
                                      s.semester_year.name == semester.name]
        return sections_matching_semester

    def __unicode__(self):
        return "%s %s" % (self.course_letters, self.course_numbers)

    class Meta:
        def __init__(self):
            pass

        app_label = 'uni_info'