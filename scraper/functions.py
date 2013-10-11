"""Contains the actual scraper functions"""

#dummy commit

from datetime import date, time
import urllib2
import urllib
import logging

from bs4 import BeautifulSoup, Tag

from scheduler.models import Course, Section, Lab, Tutorial, Lecture, Faculty,\
    AcademicInstitution, Department


# for figuring out the state of Course
STATES = {
    "Open to all students.": 0,
    "Open to all students": 0,
    "Priority to students whose programs require the course or to students in the Faculty offering the course.": 1,
    "Open only to students whose programs require the course or to students in the Faculty offering the course.": 2
}

SITE_URL = 'http://fcms.concordia.ca/fcms/asc002_stud_all.aspx'

# The ** before kwargs means "make a dictionary out of keyword arguments"
def scrape_sections(**kwargs):
    """Scrapes Concordia's class schedule page and puts the info into the
    models defined by `scheduler.models`

    Under the hood, it makes a request to the class schedule page, pulls out
    session variables, and makes a request for course schedules based on the
    parameters it receives, using defaults if no parameters are provided.
    """
    # TODO: implement multiple department lookup


    # TODO: think of a better variable name / this is ugly
    defaults = {
        'course_letters': '',
        'course_numbers': '',
        'year': date.today().year,  # This is probably flawed?
        'session': 'A',  # default is all sessions
        'departments': '04', #default for now is ENCS
        'level': 'U',
        'title': ''
    }
    for key in defaults:
        if key in kwargs:
            defaults[key] = kwargs[key]

    # The session variables that have to be pulled from the site
    required_info = ['__VIEWSTATE', '__EVENTVALIDATION']

    # Request the page (so we can grab the session variables later)
    site_tree = BeautifulSoup(urllib2.urlopen(SITE_URL))

    # populate the POST payload data
    data = {
        'ctl00$PageBody$txtCournam': defaults['course_letters'],
        'ctl00$PageBody$txtCournum': defaults['course_numbers'],
        'ctl00$PageBody$ddlYear': defaults['year'],
        'ctl00$PageBody$ddlSess': defaults['session'],
        'ctl00$PageBody$ddlLevl': defaults['year'],
        'ctl00$PageBody$ddlDept': '04',  # FIXME: this
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

    # TODO: Make this generic
    concordia = AcademicInstitution.objects.get(
        name="Concordia University",
    )

    # TODO: Make this generic
    encs = Faculty.objects.get(
        name="Engineering and Computer Science",
    )
    #encs.save()

    # TODO: Make this generic
    cse = Department.objects.get(
        name="Computer Science and Software Engineering",
    )
    #cse.save()

    while isinstance(current_row, Tag):

        # Parse Course data
        status, code, name, credits_ = current_row.contents[1:-1]
        status = STATES[status.img['title']]
        code = code.font.b.string  # grab the data
        course_letters = code[0:4]
        course_numbers = code[5:]
        name = name.font.b.string  # grab the data
        credits_ = float(credits_.font.b.string[:-7])  # grab the data, convert to float

        t = (status, code, name, credits_)

        course = Course(course_letters=course_letters, course_numbers=course_numbers,
                        name=name, course_credits=credits_, openness=status,
                        department=cse, description='')

        a = Course.objects.get(course_letters=course_letters,
                               course_numbers=course_numbers)

        if a is not None:
            course.update()
        # course.save()

        current_row = current_row.nextSibling

        while isinstance(current_row, Tag) and current_row['bgcolor'] != 'LightBlue':
            # TODO: implement this
            current_row = current_row.nextSibling
            #end of course data

            #move on to next course