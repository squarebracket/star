"""Contains the actual scraper functions"""
from datetime import date, time
import time as fmttime
import urllib2
import urllib
import logging
import re
import sys

from bs4 import BeautifulSoup, Tag

from uni_info.models import Course, Section, Faculty, AcademicInstitution, Department, Semester, Requirement, \
    Facility, Building


current_section = None

logger = logging.getLogger('scraper')

class ConcordiaScraper():

    # for figuring out the state of Course
    STATES = {
        "Open to all students.": Course.OPEN_TO_ALL,
        "Open to all students": Course.OPEN_TO_ALL,
        "Priority to students whose programs require the course or to students in the Faculty offering the course.": Course.PRIORITY_TO_SAME_FACULTY,
        "Open only to students whose programs require the course or to students in the Faculty offering the course.": Course.ONLY_OPEN_TO_SAME_FACULTY
    }

    SEMESTER_MAPPER = {
        '/2': Semester.FALL,
        '/3': Semester.YEAR_LONG,
        '/4': Semester.WINTER,
        '/1': Semester.SUMMER_1
    }

    SECTION_TYPE_MAPPER = {
        'Lect': Section.LECTURE,
        'Tut': Section.TUTORIAL,
        'Lab': Section.LAB,
        'UgradNSched': Section.UNSCHEDULED,
        'OnLine': Section.ONLINE,
        'Prac/Int/WTerm': Section.UNSCHEDULED,
        'Sem': Section.SEMINAR,
    }

    REQUIREMENTS_MAPPER = {
        'Minimum of (?P<value>\d{1,3}) credits in (.*)': Requirement.NUMBER_OF_CREDITS_COMPLETED,
        '(?P<value>\d{2}) credits in the program': Requirement.NUMBER_OF_CREDITS_COMPLETED,
    }



    PREREQ_REGEX = r"([A-Z]{4}) ([0-9A-Z]{3,6}(?:, ([0-9A-Z]{3,6}))*)"
    SECTION_REGEX = r'([-MTWJFSD]{7}) \((\d\d:\d\d)-(\d\d:\d\d)\)'
    SEC_REGEX = r'.*(\/\d) ([^\*]+) ([^\*]+) (\*Canceled\* )?([-MTWJFSD]{7}) \((\d\d:\d\d)-(\d\d:\d\d)\)(?: Week\((\d)\))? (LOY|SGW)? (?:([A-Z]*)-([A-Z]?[\d\. ]*) )?(.*)'
    DESC_REGEX = r"""
    <b><font color="#303030">([A-Z]{4}) (\d{3})<\/font><\/b><i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b><font color="#303030">(.*)<\/font><\/b><\/i>\([0-9\.] credits\) <br \/>\nPrerequisite: (.*?)\. (.*)<br \/>
    """

    SECTIONS_URL = 'http://fcms.concordia.ca/fcms/asc002_stud_all.aspx'

    # TODO: think of a better variable name / this is ugly
    defaults = {
        'course_letters': '',
        'course_numbers': '',
        'year': date.today().year,  # This is flawed
        'session': 'A',  # default is all sessions
        'departments': Department.objects.filter(code__startswith=04),  # default for now is ENCS
        'department': None,  # TODO: explain this
        'level': 'U',
        'title': ''
    }

    # The session variables that have to be pulled from the site
    required_info = ['__VIEWSTATE', '__EVENTVALIDATION']

    def __init__(self):
        self.site_tree = None
        self.get_site_tree()
        # TODO: Make this generic
        self.institution = AcademicInstitution.objects.get(name="Concordia University")
        self.num_courses = 0
        self.num_sections = 0
        self.num_cancelled = 0
        self.parent_section = [None] *3
        self.current_course = None
        self.current_section = None
        self.current_row = None
        self.current_department = None

    def get_site_tree(self, payload_data=None):
        # URL-encode payload for sending
        if payload_data is not None:
            payload_data = urllib.urlencode(payload_data)
            self.site_tree = BeautifulSoup(urllib2.urlopen(self.SECTIONS_URL, payload_data))
        else:
            self.site_tree = BeautifulSoup(urllib2.urlopen(self.SECTIONS_URL))

    def create_payload(self, payload_data):
        data = {
            'ctl00$PageBody$txtCournam': payload_data['course_letters'],
            'ctl00$PageBody$txtCournum': payload_data['course_numbers'],
            'ctl00$PageBody$ddlYear': payload_data['year'],
            'ctl00$PageBody$ddlSess': payload_data['session'],
            'ctl00$PageBody$ddlLevl': payload_data['level'],
            'ctl00$PageBody$ddlDept': payload_data['department'],
            'ctl00$PageBody$txtKeyTtle': payload_data['title'],
            '__EVENTTARGET': 'ctl00$PageBody$btn_ShowScCrs',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': ''
        }
        # adds the required session variables to the payload data
        for el in self.required_info:
            data[el] = self.extract_session_var(el)
        return data

    def extract_session_var(self, element):
        return self.site_tree.find('input', id=element)['value']

    def process_course(self):
        # Parse Course data
        status, code, name, credits_ = self.current_row.contents[1:-1]
        status = self.STATES[status.img['title']]
        code = code.font.b.string  # grab the data
        course_letters = code[0:4]
        course_numbers = code[5:]
        name = name.font.b.string  # grab the data
        credits_ = float(credits_.font.b.string[:-7])  # grab the data, convert to float
        logger.info("found course %s %s" % (course_letters, course_numbers))

        try:
            course = Course.objects.get(course_letters=course_letters,
                                        course_numbers=course_numbers,)
        except Course.DoesNotExist:
            course = Course(course_letters=course_letters,
                            course_numbers=course_numbers)
        course.name = name
        course.course_credits = credits_
        course.openness = status
        course.department = self.current_department
        course.description = ''
        course.save()

        return course

    # The ** before kwargs means "make a dictionary out of keyword arguments"
    def scrape_sections(self, **kwargs):
        """
        Scrapes Concordia's class schedule page and puts the info into the
        models defined by `uni_info`

        Under the hood, it makes a request to the class schedule page, pulls out
        session variables, and makes a request for course schedules based on the
        parameters it receives, using defaults if no parameters are provided.

        The information it extracts is inserted into :model:`uni_info.Course` and
        :model:`uni_info.Section` instances.
        """

        # TODO: implement error handling
        if 'faculty' not in kwargs or 'departments' not in kwargs:
            self.get_departments()

        params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
        params.update(self.defaults)

        print "Scraping course data for %d departments" % len(params['departments'])

        for department in params['departments']:
            self.current_department = department
            self.year = params['year']
            print "Scraping course data for %s" % department.name

            # populate the POST payload data
            params['department'] = '%04d' % department.code
            payload_data = self.create_payload(params)

            # Try to get the course data!
            # TODO: this needs error handling
            self.get_site_tree(payload_data)

            # Get the table of courses from the site tree
            table = self.site_tree.find('table', id='ctl00_PageBody_tblBodyShow1')
            self.current_row = table.find('tr', bgcolor='LightBlue')

            # loop through courses
            while isinstance(self.current_row, Tag):
                # increment course counter
                self.num_courses += 1
                # update courses on terminal
                sys.stdout.write('Number of courses found: %d \r' % self.num_courses)
                sys.stdout.flush()

                self.current_course = self.process_course()

                self.current_row = self.current_row.nextSibling
                # should be a while test_thing()
                while isinstance(self.current_row, Tag) and \
                                self.current_row['bgcolor'] != 'LightBlue':

                    try:
                        row_as_string = self.gen_string_from_current_row()
                        logger.info('row as string: %s' % row_as_string)
                        # if prereq row
                        if 'Prerequisite:' in row_as_string:
                            prereq_string = row_as_string[15:]
                            self.current_course.save_scraped_prerequisite_text(prereq_string)
                            requirements = self.process_requirements_string(prereq_string)

                        self.current_row = self.current_row.nextSibling
                        self.current_course.save()
                        #end of prereq handling
                    except StandardError:
                        # print current_row
                        self.current_row = self.current_row.nextSibling
                        pass
                    # if section info
                    m = re.search(self.SECTION_REGEX, unicode(self.current_row))
                    if m is not None:
                        self.process_section()
                #move on to next course

            print "Scraped data for %d courses in %d sections, %d of which were cancelled" % (self.num_courses, self.num_sections,
                                                                                              self.num_cancelled)

    def get_departments(self):

        if not self.site_tree:
            self.get_site_tree()

        dept_and_fac = self.site_tree.find('select', id='ctl00_PageBody_ddlDept')

        # NOTE: the following code is inefficient. I've left it like this since
        # it probably won't be run often.
        for o in dept_and_fac:
            if isinstance(o, Tag):
                code = o['value']
                name = o.string.lstrip('- ')
                if len(code) < 4:
                    # it's a faculty
                    try:
                        faculty = Faculty.objects.get(code=code)
                    except Faculty.DoesNotExist:
                        faculty = Faculty(code=code, name=name,
                                          university=self.institution,
                                          description='')
                        faculty.save()
                else:
                    # FIXME: does not have robust error checking on putting in
                    # right faculty
                    try:
                        Department.objects.get(code=code)
                    except Department.DoesNotExist:
                        dept = Department(code=code, name=name, faculty=faculty)
                        dept.save()


    def process_requirements_string(self, req_string):

        logger.info("Prerequisite string: %s" % req_string)

        prereq_courses_list = []
        coreq_courses_list = []
        other_requirements_list = []

        split_string = req_string.split('; ')
        for requirement_set in split_string:
            logger.info('testing string (split by ;) %s' % requirement_set)
            # if it starts with [A-Z]{4}, it's a set of courses
            if re.match('^[A-Z]{4}(.)*', requirement_set):
                for c in requirement_set.split(', '):
                    logger.info('testing string (split by ,) %s' % c)
                    m = re.match('([A-Z]{4} )?(\d{3})(.*)', c)
                    if m is not None:
                        if m.group(1) is not None:
                            course_letters = m.group(1).strip(' ')
                        course_numbers = m.group(2)
                        prereq_courses_list.append((course_letters, course_numbers))
                        logger.info('testing remainder string %s' % m.group(3).lower().strip(' .'))
                        if m.group(3).lower().strip(' .') == "previously or concurrently":
                            coreq_courses_list.append(prereq_courses_list.pop())
                            pass
                    if c == "previously or concurrently":
                        coreq_courses_list.append(prereq_courses_list.pop())
            # if not, it's another kind of requirement
            else:
                for (regex, req_num) in self.REQUIREMENTS_MAPPER.iteritems():
                    m = re.match(regex, requirement_set)
                    if m is not None:
                        other_req = (req_num, m.groupdict())
                        other_requirements_list.append(other_req)
                        break
                else:
                    # other_requirements_list.append('unknown other requirement')
                    print "unhandled other requirement of %s" % requirement_set
        logger.info("Prereqs found: %s; Coreqs found: %s; Other requirements found: %s" %
                     (prereq_courses_list, coreq_courses_list, other_requirements_list))

        all_requirements = []

        for prereq in prereq_courses_list:
            try:
                prereq_course = Course.objects.get(course_letters=prereq[0],
                                                   course_numbers=prereq[1])
                r = Requirement(type=Requirement.PREVIOUSLY_TAKEN)
                r = r.get_or_create(prereq_course)
                self.current_course.requirements.add(r)
                all_requirements.append(r)
            except Course.DoesNotExist:
                print 'course %s %s does not exist' % (prereq[0], prereq[1])
        for coreq in coreq_courses_list:
            try:
                coreq_course = Course.objects.get(course_letters=coreq[0],
                                                  course_numbers=coreq[1])
                r = Requirement(type=Requirement.CONCURRENTLY_TAKEN)
                r = r.get_or_create(coreq_course)
                self.current_course.requirements.add(r)
                all_requirements.append(r)
            except Course.DoesNotExist:
                print 'course %s %s does not exist' % (coreq[0], coreq[1])
        for other_req in other_requirements_list:
            value = other_req[1]['value']
            try:
                r = Requirement.objects.get(type=other_req[0],
                                            _value=value)
            except Requirement.DoesNotExist:
                r = Requirement(type=other_req[0],
                                _value=value)
                r.save()
            self.current_course.requirements.add(r)
            all_requirements.append(r)

        return all_requirements

    def process_section(self):

        self.num_sections += 1

        section_string = self.gen_string_from_current_row()
        logger.info(section_string)

        # execute gigantic regex
        m = re.match(self.SEC_REGEX, section_string)

        sem = self.SEMESTER_MAPPER[m.group(1)]
        semester = Semester.objects.get(period=sem, year=self.year)

        sec_type = self.SECTION_TYPE_MAPPER[m.group(2)]
        name = m.group(3)

        cancelled = m.group(4) == '*Canceled*'
        if cancelled:
            self.num_cancelled += 1

        # get days on which section takes place
        days = m.group(5).replace('-', '')
        # get section start time
        t = fmttime.strptime(m.group(6), '%H:%M')
        start_time = time(*t[3:6])
        # get section end time
        t = fmttime.strptime(m.group(7), '%H:%M')
        end_time = time(*t[3:6])
        # week info
        week = m.group(8)
        # get location info
        campus = m.group(9)
        bldg = m.group(10)
        room = m.group(11)

        instructor = m.group(12)

        # the section data used here should never change
        (self.current_section, created) = \
            Section.objects.get_or_create(course=self.current_course,
                                          semester_year=semester,
                                          name=name, sec_type=sec_type)
        # this data may change -- so update it each scrape
        self.current_section.days = days
        self.current_section.cancelled = cancelled
        self.current_section.start_time = start_time
        self.current_section.end_time = end_time
        self.current_section.week = week
        self.current_section.instructor_text = instructor

        if bldg:
            building = Building.objects.get(name=bldg)
            (location, created) = \
                Facility.objects.get_or_create(name=room.replace(' ', '-'),
                                               building=building)
            self.current_section.location = location

        string = self.current_row.get_text().encode('unicode-escape')
        m = re.match('^(.*)(/\d)(\s*)', string.replace('\\xa0', ' '))
        if len(m.group(3)) == 0:
            depth = 0
        elif len(m.group(3)) == 3:
            depth = 1
        elif len(m.group(3)) == 6:
            depth = 2
        else:
            raise StandardError

        if depth > 0:
            self.current_section.parent_section = self.parent_section[depth-1]

        self.current_section.save()

        logger.info('Parsed section as: %s' % Section.objects.filter(
            pk=self.current_section.pk).values())

        self.parent_section[depth] = self.current_section

    def gen_string_from_current_row(self):
        b = []
        for a in self.current_row.contents:
            if type(a) is Tag:
                # this sub is dangerous.... keep an eye out.
                to_append = re.sub('[ ]{2,10}', ' ', a.get_text().strip())
                b.append(to_append)
            #keeping this section just in case it's needed for other faculties
            #else:
            #    if a.strip() != u'':
            #        c = 'durr %s' % a.strip().replace('        ', ' ')
            #        b.append(c)
        return ' '.join(b)