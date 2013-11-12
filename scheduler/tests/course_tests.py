from django.test import TestCase
from uni_info.models import Course


class CourseTest(TestCase):
    def test_should_filter_by_name_and_section(self):

        course_list = Course.search_by_regex(r'SOEN')
        semester_list = [4]
        sections_by_semester = []

        for course in course_list:
            for semester in semester_list:
                sections_by_semester.extend(course.get_sections_for_semester(semester))

        print sections_by_semester