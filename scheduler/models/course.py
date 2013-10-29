from django.db import models
from scheduler.models.department import Department


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

        app_label = 'scheduler'