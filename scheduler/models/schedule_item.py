from django.db import models
from uni_info.models import Section, Course, Semester


class ScheduleItem():

    def __init__(self, section_list):
        self.sections = section_list
        self.semester = section_list[0].semester_year
        self.course = section_list[0].course
    
    def conflicts_with(self, other):
        # print type(other)
        # if type(other) is not ScheduleSlice:
        #     raise TypeError
        if self.course == other.course:
            return True
        for this_section in self.sections:
            for other_section in other.sections:
                # print 'comparing', this_section, 'and', other_section
                # compare days
                for day in this_section.days:
                    if day in other_section.days:
                        # days conflict between sections
                        # break out of this loop to compare actual times
                        # print 'overlap on', day
                        if this_section.start_time <= other_section.start_time <= this_section.end_time:
                            # print 'start time of', other_section, 'is between start/end of', this_section, 'on', day
                            # print 'section', this_section, 'conflicts with', other_section
                            return True
                        if this_section.start_time <= other_section.end_time <= this_section.end_time:
                            # print 'end time of', other_section, 'is between start/end of', this_section, 'on', day
                            # print 'section', this_section, 'conflicts with', other_section
                            return True
                        if other_section.start_time <= this_section.start_time <= other_section.end_time:
                            # print 'start time of', this_section, 'is between start/end of', other_section, 'on', day
                            # print 'section', this_section, 'conflicts with', other_section
                            return True
                        if other_section.start_time <= this_section.end_time <= other_section.end_time:
                            # print 'end time of', this_section, 'is between start/end of', other_section, 'on', day
                            # print 'section', this_section, 'conflicts with', other_section
                            return True
                        # print "no time conflict between", this_section, 'and', other_section, 'on', day

                else:
                    # days don't conflict between this_section & other_section
                    # print "days", this_section.days, 'and', other_section.days, "don't overlap"
                    pass

        # print 'no contact between slice', self, 'and', other
        return False

    def print_it(self):
        l = []
        for sec in self.sections:
            l.append(sec)
        print l

    def section_names(self):
        r = []
        for sec in self.sections:
            r.append(sec.name)
        return '-'.join(r)

    def __str__(self):
        return "%s %s: %s" % (self.course.course_letters,
                               self.course.course_numbers,
                               self.section_names())

    def __repr__(self):
        return "%s %s: %s" % (self.course.course_letters,
                               self.course.course_numbers,
                               self.section_names())

    class Meta:
        def __init__(self):
            pass

        # app_label = 'scheduler'