"""Contains the actual scraper functions"""
from datetime import date, time
import time as fmttime
import urllib2
import urllib
import logging
import re
import sys
import os

from bs4 import BeautifulSoup, Tag

from uni_info.models import Course, Section, Faculty, AcademicInstitution, Department, Semester
#from scheduler.models import Course, Section, Lab, Tutorial, Lecture, Faculty,\
#    AcademicInstitution, Department, Semester, ScheduleItem

#logger = logging.getLogger(__name__)
#logfilename = os.path.join(os.getcwd(), 'scraper.log')
## configure the logging
#FORMAT = \
#    """%(levelname)s @ %(asctime)-15s : %(message)s
#    called from %(pathname)s at line %(lineno)d"""
#formatter = logging.Formatter(fmt=FORMAT)
#handler = logging.Handler()
#handler.setFormatter(formatter)
##logger.basicConfig(filename=logfilename, level=logging.DEBUG, format=FORMAT)

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

SITE_URL = 'http://fcms.concordia.ca/fcms/asc002_stud_all.aspx'

PREREQ_REGEX = "([A-Z]{4}) ([0-9A-Z]{3,6}(?:, ([0-9A-Z]{3,6}))*)"
SECTION_REGEX = '([-MTWJFSD]{7}) \((\d\d:\d\d)-(\d\d:\d\d)\)'

current_section = None


# The ** before kwargs means "make a dictionary out of keyword arguments"
def scrape_sections(**kwargs):
    """
    Scrapes Concordia's class schedule page and puts the info into the
    models defined by `scheduler.models`

    Under the hood, it makes a request to the class schedule page, pulls out
    session variables, and makes a request for course schedules based on the
    parameters it receives, using defaults if no parameters are provided.
    """

    # Request the page (so we can grab the session variables later)
    site_tree = BeautifulSoup(urllib2.urlopen(SITE_URL))

    # TODO: implement error handling
    if 'faculty' not in kwargs or 'department' not in kwargs:
        get_departments(site_tree)

    # TODO: think of a better variable name / this is ugly
    defaults = {
        'course_letters': '',
        'course_numbers': '',
        'year': date.today().year,  # This is flawed
        'session': 'A',  # default is all sessions
        'departments': Department.objects.filter(code__startswith=04),  # default for now is ENCS
        'level': 'U',
        'title': ''
    }

    params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
    params.update(defaults)
    #for key in defaults:
    #    if key in kwargs:
    #        to_post[key] = kwargs[key]
    #    else:
    #        to_post[key] = defaults[key]

    # The session variables that have to be pulled from the site
    required_info = ['__VIEWSTATE', '__EVENTVALIDATION']

    print "Scraping course data for %d departments" % len(params['departments'])

    for department in params['departments']:
        print "Scraping course data for %s" % department.name
        # populate the POST payload data
        data = {
            'ctl00$PageBody$txtCournam': defaults['course_letters'],
            'ctl00$PageBody$txtCournum': defaults['course_numbers'],
            'ctl00$PageBody$ddlYear': defaults['year'],
            'ctl00$PageBody$ddlSess': defaults['session'],
            'ctl00$PageBody$ddlLevl': defaults['level'],
            'ctl00$PageBody$ddlDept': '%04d' % department.code,  # FIXME: this
            'ctl00$PageBody$txtKeyTtle': defaults['title'],
            '__EVENTTARGET': 'ctl00$PageBody$btn_ShowScCrs',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': ''
        }

        # adds the required session variables to the payload data
        for el in required_info:
            data[el] = site_tree.find('input', id=el)['value']

        # URL-encode payload for sending
        data = urllib.urlencode(data)

        # Try to get the course data!
        # TODO: this needs error handling
        site_tree = BeautifulSoup(urllib2.urlopen(SITE_URL, data))

        # Get the table of courses from the site tree
        table = site_tree.find('table', id='ctl00_PageBody_tblBodyShow1')
        current_row = table.find('tr', bgcolor='LightBlue')

        num_courses = 0
        num_sections = 0
        num_cancelled = 0
        # loop through courses
        while isinstance(current_row, Tag):
            # increment course counter
            num_courses += 1
            # update courses on terminal
            sys.stdout.write('Number of courses found: %d \r' % num_courses)
            sys.stdout.flush()

            # Parse Course data
            status, code, name, credits_ = current_row.contents[1:-1]
            status = STATES[status.img['title']]
            code = code.font.b.string  # grab the data
            course_letters = code[0:4]
            course_numbers = code[5:]
            name = name.font.b.string  # grab the data
            credits_ = float(credits_.font.b.string[:-7])  # grab the data, convert to float
            logging.info("found course %s %s" % (course_letters, course_numbers))

            try:
                course = Course.objects.get(course_letters=course_letters,
                                            course_numbers=course_numbers)
            except Course.DoesNotExist:
                course = Course(course_letters=course_letters,
                                course_numbers=course_numbers,
                                name=name, course_credits=credits_,
                                openness=status,
                                department=department, description='')
                course.save()

            current_row = current_row.nextSibling
            parent_section = [None] *3
            while isinstance(current_row, Tag) and current_row['bgcolor'] != 'LightBlue':

                try:
                    # if prereq row
                    if len(current_row.contents) > 2 and \
                                    "Prerequisite:" in current_row.contents[2].string:
                        prereq_string = current_row.contents[3].string
                        course._scraped_prerequisite_text = prereq_string
                        (prereqs, coreqs, others) = split_prereq_string(prereq_string)
                        for prereq in prereqs:
                            try:
                                prereq_course = Course.objects.get(course_letters=prereq[0],
                                                            course_numbers=prereq[1])
                                course.prerequisite_courses.add(prereq_course)
                            except Course.DoesNotExist:
                                pass
                        for coreq in coreqs:
                            try:
                                coreq_course = Course.objects.get(course_letters=coreq[0],
                                                            course_numbers=coreq[1])
                                course.corequisite_courses.add(coreq_course)
                            except Course.DoesNotExist:
                                pass
                    current_row = current_row.nextSibling
                    course.save()
                    #end of prereq handling
                except BaseException:
                    # print current_row
                    pass
                # if section info
                m = re.search(SECTION_REGEX, unicode(current_row))
                if m is not None:
                    num_sections += 1

                    # get days on which section takes place
                    days = m.group(1).replace('-', '')

                    # get section start time
                    t = fmttime.strptime(m.group(2), '%H:%M')
                    start_time = time(*t[3:6])

                    # get section end time
                    t = fmttime.strptime(m.group(3), '%H:%M')
                    end_time = time(*t[3:6])

                    # get semester data -- here we assume year
                    # TODO: handle year properly
                    s = SEMESTER_MAPPER[current_row.contents[2].string.strip()]
                    semester = Semester.objects.get(period=s, year=2013)

                    # get section type data. Concordia makes ugly cody, so this is ugly.
                    d = []
                    for fucking_christ in current_row.contents[3].font.find_all('b'):
                        d.append(fucking_christ.string)
                    d = ' '.join(d)
                    d = d.split(' ')

                    try:
                        c = Section.objects.get(course=course, name=d[1], semester_year=semester)
                        c.start_time = start_time
                        c.end_time = end_time
                    except Section.DoesNotExist:
                        c = Section(name=d[1], days=days, start_time=start_time, end_time=end_time,
                                    semester_year=semester, course=course, sec_type=SECTION_TYPE_MAPPER[d[0]])

                    # get nesting level. Once again, ugly code -> ugly code
                    blah = current_row.contents[3].font.contents[0].string.encode('unicode-escape')
                    if blah == u'\xa0\xa0\xa0\xa0\xa0\xa0'.encode('unicode-escape'):
                        depth = 2
                    elif blah == u'\xa0\xa0\xa0'.encode('unicode-escape'):
                        depth = 1
                    else:
                        depth = 0
                    parent_section[depth] = c
                    if depth > 0:
                        c.parent_section = parent_section[depth-1]

                    # check to see if the section is cancelled
                    if u'*Canceled*'.encode('unicode-escape') in d:
                        c.cancelled = True
                        num_cancelled += 1

                    c.save()
            #move on to next course

        print "Scraped data for %d courses in %d sections, %d of which were cancelled" % (num_courses, num_sections,
                                                                                          num_cancelled)


# the argument exists for efficiency; requesting the site takes a long time
def get_departments(site_tree=None):

    # TODO: Make this generic
    concordia = AcademicInstitution.objects.get(
        name="Concordia University",
    )

    if not site_tree:
        # Request the page
        site_tree = BeautifulSoup(urllib2.urlopen(SITE_URL))

    dept_and_fac = site_tree.find('select', id='ctl00_PageBody_ddlDept')

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
                                      university=concordia, description='')
                    faculty.save()
                #faculty = Faculty.objects.get_or_create(code=code, name=name,
                #                                        university=concordia,
                #                                        description='')
            else:
                try:
                    Department.objects.get(code=code)
                except Department.DoesNotExist:
                    dept = Department(code=code, name=name, faculty=faculty)
                    dept.save()

OTHER_REQUIREMENTS_LIST = {

}


def split_prereq_string(prereq_string):

    logging.info("Prerequisite string: %s" % prereq_string)

    prereq_courses_list = []
    coreq_courses_list = []
    other_requirements_list = []

    split_string = prereq_string.split('; ')
    for requirement_set in split_string:
        # if it starts with [A-Z]{4}, it's a set of courses
        if re.match('^[A-Z]{4}(.)*', requirement_set):
            for c in requirement_set.split(', '):
                m = re.match('([A-Z]{4} )?(\d{3})(.*)', c)
                if m is not None:
                    if m.group(1) is not None:
                        course_letters = m.group(1).strip(' ')
                    course_numbers = m.group(2)
                    prereq_courses_list.append((course_letters, course_numbers))
                    if m.group(3).lower().strip(' .') == "previously or concurrently":
                        coreq_courses_list.append(prereq_courses_list.pop())
                        pass
                if c == "previously or concurrently":
                    coreq_courses_list.append(prereq_courses_list.pop())
        # if not, it's another kind of requirement
        else:
            other_requirements_list.append(requirement_set)

    logging.info("Prereqs found: %s; Coreqs found: %s; Other requirements found: %s" %
                 (prereq_courses_list, coreq_courses_list, other_requirements_list))
    return prereq_courses_list, coreq_courses_list, other_requirements_list
