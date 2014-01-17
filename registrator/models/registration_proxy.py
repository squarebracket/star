from registrator.models.registration_entry import RegistrationEntry
from uni_info.models import Section


class RegistrationProxy(RegistrationEntry):
    """
    Proxy class which handles actually doing the registration in a system
    of a :model:`registrator.RegistrationEntry`
    """

    # I guess functions for registration in Concordia's system would go here?

    def add_schedule_item(self, schedule_item):
        section_list = schedule_item.sections
        sections = {}
        sections['MainSec'] = section_list[0]
        for i in range(1, len(section_list)):
            sections['RelSec' + str(i)] = section_list[i]
        sections['course_letters'] = section_list[0].course.course_letters
        sections['course_numbers'] = section_list[0].course.course_numbers
        sections['session'] = section_list[0].semester_year
        sections['CatNum'] = '12345'
        sections['Start'] = section_list[0].start_time
        sections['Finish'] = section_list[0].end_time
        sections['Campus'] = 'S'
        sections['Title'] = section_list[0].course.name
        return sections


    class Meta:
        proxy = True