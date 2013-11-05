from uni_info.models import Course, Section
from django.db.models.query import QuerySet
from scheduler.models import ScheduleItem

class ScheduleGenerator():

    """
    Generates possible schedules based on a list of courses

    The
    """

    possibilities = {}
    possiblesched = {}

    def __init__(self, list_of_courses, semester):

        self.courses = list_of_courses
        self.semester = semester

    def generate_schedule(self):
        pass


def get_section_permutations(object, **kwargs):
    """
    Return all possible child section permutations for a given
    :model:`uni_info.Course` or :model:`uni_info.Section`
    """
    if type(object) == Course:
        aggregation = []
        top_levels = [_get_permutations_from_section(m) for m in object.section_set.filter(parent_section=None, **kwargs)]
        for section in top_levels:
            if type(section) is list:
                    aggregation.extend(section)
            else:
                aggregation.append([section])
        return aggregation
    elif type(object) == Section:
        return _get_permutations_from_section(object)
    elif type(object) == QuerySet:
        aggregation = []
        top_levels = [_get_permutations_from_section(m) for m in object]
        for section in top_levels:
            aggregation.extend(section)
        return aggregation


def _get_permutations_from_section(section):
    """
    Returns all possible section permutations for a given parent section

    Generally this shouldn't be called manually; You probably want to use
    the course interface instead
    """
    direct_descendants = [_get_permutations_from_section(m) for m in section.section_set.all()]
    # no direct descendants means we're at the leaf, so return it
    if len(direct_descendants) == 0:
        return section
    # this next part adds the parent section to the possibilities
    else:
        # temporary list for aggregating all possibilities
        l = []
        for i in direct_descendants:
            # i is only a list when it is a nested list, in which case we
            # need to aggregate the sub-lists
            if type(i) == list:
                for k in i:
                    k.insert(0, section)
                    l.append(k)
            # if it's not a list, it's a simple Section object, so add this
            # parent section the possibilities list
            else:
                l.append([section, i])
        return l