from django.test import TestCase
from uni_info.models import Course


class CourseTest(TestCase):
    def test_should_filter_by_name(self):

        Course.search_by_regex(r'SOEN')