import time
from uni_info.models import Course, Section
from django.db.models.query import QuerySet
from scheduler.models.schedule_item import ScheduleItem
from scheduler.models import ScheduleItem, SemesterSchedule, ScheduleConstraintSet


class ScheduleGenerator(object):
    """
    Generates possible schedules
    """

    def __init__(self, list_of_courses=[], semester=None, constraint_set=None):

        self.courses = list_of_courses
        self.semester = semester
        self.constraint_set = constraint_set
        self.possibilities = []
        self.possiblesched = []
        self.goodscheds = []

    def generate_schedules(self):
        """
        Generate all possible schedules based on instance data
        """

        if not self.courses:
            return []  # TODO: make this a real exception

        # reset instance data used in schedule generation
        self.possibilities = []
        self.possiblesched = []
        self.goodscheds = []
        for course in self.courses:
            self.possibilities.append(get_slices_for_course(course, semester_year=self.semester))

        if self.constraint_set:
            self.possibilities = apply_constraints_to_slices(self.possibilities, self.constraint_set)

        self.possiblesched = build_possible_schedules(self.possibilities)
        self.goodscheds = get_working_schedules(self.possiblesched)

        return [SemesterSchedule(schedule_items=sched) for sched in self.goodscheds]

    def add_constraint(self, constraint):
        if not self.constraint_set:
            self.constraint_set = ScheduleConstraintSet(name='whatever')
            self.constraint_set.save()
            constraint.con_set = self.constraint_set
        else:
            constraint.con_set = self.constraint_set

    def add_course(self, course):
        self.courses.append(course)

    def remove_course(self, course):
        self.courses.remove(course)


def get_slices_for_course(course, **kwargs):
    return get_slices_from_permutations(get_section_permutations(course, **kwargs))


def get_slices_from_permutations(permutations):
    """
    Returns a list of :model:`ScheduleItem`s for a given list of permutations
    """
    slice_set = []
    for permutation in permutations:
        slice = ScheduleItem(permutation)
        slice_set.append(slice)
    return slice_set


def apply_constraints_to_slices(course_slices, constraint_set):
    constrained_slices = []
    for course in course_slices:
        course_copy = list(course)
        for slice in course:
            for constraint in constraint_set:
                if slice.conflicts_with(constraint):
                    course_copy.remove(slice)
                    break
        constrained_slices.append(course_copy)
    return constrained_slices


def get_section_permutations(obj, **kwargs):
    """
    Return all possible child section permutations for a given
    :model:`uni_info.Course` or :model:`uni_info.Section`
    """
    if type(obj) == Course:
        aggregation = []
        top_levels = [_get_permutations_from_section(m) for m in obj.section_set.filter(parent_section=None, **kwargs)]
        for section in top_levels:
            if type(section) is list:
                    aggregation.extend(section)
            else:
                aggregation.append([section])
        # return aggregation
    elif type(obj) == Section:
        aggregation = _get_permutations_from_section(obj)
    elif type(obj) == QuerySet:
        aggregation = []
        top_levels = [_get_permutations_from_section(m) for m in obj]
        for section in top_levels:
            aggregation.extend(section)
        # return aggregation

    return aggregation


def _get_permutations_from_section(section):
    """
    Returns all possible section permutations for a given parent section

    Generally this shouldn't be called manually; You probably want to use
    the non-_'ed interface instead
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
                    # slice = ScheduleSlice(k)
                    # print slice.print_it()
                    l.append(k)
                    # l.append(slice)
                    # print 'k', k
            # if it's not a list, it's a simple Section object, so add this
            # parent section the possibilities list
            else:
                # print 'i', i
                l.append([section, i])
        # slice = ScheduleSlice(l)
        return l


def build_possible_schedules(list_of_slices):
    """
    Return a list consisting of all possible combinations of
    :model:`scheduler.ScheduleItem`

    TODO: make this docstring proper
    """
    top_levels = []
    for m in list_of_slices[0]:
        top_levels.extend(_build_possible_schedules(m, list_of_slices, 1))

    return top_levels


def _build_possible_schedules(section, list_of_slices, depth):
    """
    TODO: write this docstring
    """
    if depth < len(list_of_slices):
        direct_descendants = [_build_possible_schedules(m, list_of_slices, depth+1) for m in list_of_slices[depth]]
    else:
        return section
    # this next part adds the parent section to the possibilities
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
    # print l
    return l


def get_working_schedules(slices):
    """
    Return list of all non-overlapping :model:`scheduler.ScheduleItem`s
    """
    good_scheds = []
    #time_start = time.clock()
    for a in slices:
        if recursively_try_items(a):
            good_scheds.append(a)
    #time_end = time.clock()
    # print 'took %f seconds' % (time_end - time_start)
    return good_scheds


def recursively_try_items(blah):
    """
    Recursively tests :model:`scheduler.ScheduleItem`s that are passed in
    to see if they conflict with each other

    Works by comparing all possible unordered items.

    For example, for recursively_try_items([A, B, C, D]), it compares
    AB, AC, AD, then calls itself recursively with [B, C, D] as the argument.
    """
    if len(blah) > 2:
        for i in range(0, len(blah)-1):
            if blah[0].conflicts_with(blah[i+1]):
                # CONFLICT!
                return False
        else:
            return recursively_try_items(blah[1:])
    else:
        if blah[0].conflicts_with(blah[1]):
            # CONFLICT!
            return False
    return True