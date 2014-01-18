from registrator.models import StudentRecord
from user_stuff.models import StarUser, Student
from bs4 import BeautifulSoup, Tag
from cookielib import CookieJar
import urllib
import urllib2
import urlparse
from StringIO import StringIO
import gzip
import re

from uni_info.models import Semester, Section, Course
from registrator.models import StudentRecord, StudentRecordEntry


class MyConcordiaBackend(object):

    def __init__(self):
        pass

    @staticmethod
    def authenticate(username=None, password=None, session=None):
        reg = MyConcordiaAccessor()
        if not reg.login(username, password):
            return None
        #implicit else:
        student = reg.get_user_status()
        print student
        if student:
            try:
                user = Student.objects.get(username=username)
            except Student.DoesNotExist:
                user = Student(username=username,
                               password='get from myconcordiaacc',
                               date_of_birth='1970-01-01')
                user.save()
            stud = StudentRecord.objects.get_or_create(
                student=user,
                _standing='Good'
            )
            stud_info, stud_recs = reg.parse_student_record(user)
            print stud_info
            user.date_of_birth = stud_info['date_of_birth']
            user.first_name = stud_info['first_name']
            user.last_name = stud_info['last_name']
            user.student_identifier = stud_info['id']
            user.gender = stud_info['gender']
            user.save()

        else:
            try:
                user = StarUser.objects.get(username=username)
            except StarUser.DoesNotExist:
                user = StarUser(username=username, password='get from myconcordiaacc',
                                date_of_birth='1970-01-01')
                user.save()
        session.reg = reg
        return user

    @staticmethod
    def get_user(user_id):
        try:
            return StarUser.objects.get(pk=user_id)
        except StarUser.DoesNotExist:
            return None

SEMESTER_MAPPER = {
    '/2': Semester.FALL,
    '/3': Semester.YEAR_LONG,
    '/4': Semester.WINTER,
    '/1': Semester.SUMMER_1
}


class MyConcordiaAccessor():

    LOGIN_URL = 'https://my.concordia.ca/psp/portprod/?cmd=login&languageCd=ENG'
    STUDENT_RECORD_LINK = 'Display the student record.'
    #ACADEMIC_LINK = 'Academic'
    ACADEMIC_LINK = 'Academic'
    STUDENT_RECORD_REGEX = r'([A-Z]{4}) (\d{3}[A-Z]?) (\/\d) ([A-Z0-9]*) (.*) (\d\.\d\d) ([A-Z]*[-+]?)? ([A-Z]*) \(?(\d\.\d)?\)? (\d.\d\d)? (\d*) (\d\.\d\d)? (.*)'
    REGISTRATION_NETLOC = 'regsis.concordia.ca'
    LOGIN_FAILURE_URL = 'https://my.concordia.ca/psp/portprod/?cmd=login&languageCd=ENG'
    DEFAULT_HEADERS = [
        ('Host', 'my.concordia.ca'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('Accept-Encoding', 'gzip,deflate,sdch'),
        ('Accept-Language', 'en-GB,en;q=0.8,fr;q=0.6,en-US;q=0.4,fr-CA;q=0.2'),
        ('Origin', 'https://www.myconcordia.ca'),
        ('Referer', 'https://www.myconcordia.ca/'),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36')
    ]

    def __init__(self):
        self.cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [
            ('Host', 'my.concordia.ca:443'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding', 'gzip,deflate,sdch'),
            ('Accept-Language', 'en-GB,en;q=0.8,fr;q=0.6,en-US;q=0.4,fr-CA;q=0.2'),
            ('Origin', 'https://www.myconcordia.ca'),
            ('Referer', 'https://www.myconcordia.ca/'),
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36')
        ]
        self.site_tree = None
        self.student_record = None
        #self.currently_at = {
        #    'host': None,
        #    'selector': None,
        #    'all': None
        #}
        self.currently_at = None
        self.current_bs = None

    def set_headers(self):
        if self.currently_at:
            parse = urlparse.urlparse(self.currently_at)
            origin = parse[0] + '://' + parse[1]
            self.opener.addheaders[0] = ('Host', parse[1])
            self.opener.addheaders[4] = ('Origin', origin)
            self.opener.addheaders[5] = ('Referer', self.currently_at)

    def login(self, userid, password):
        payload_data = {
            'resource': '/content/cspace/en/login.html',
            '_charset_': 'UTF-8',
            'userid': userid,
            'pwd': password
        }
        content = self.get_url(self.LOGIN_URL, payload_data)
        if self.currently_at == self.LOGIN_FAILURE_URL:
            # we didn't authenticate properly, so we have to reset the object
            self.__init__()
            return False
        else:
            self.site_tree = BeautifulSoup(content)
            return True

    def get_url(self, url, payload_data=None):
        # Todo: make this more robust?
        # Todo: also add an error condition for if an absolute URL is never supplied
        if url[:4] != 'http':
            url = urlparse.urljoin(self.currently_at, url)
        self.set_headers()
        if payload_data:
            data = urllib.urlencode(payload_data)
            response = self.opener.open(url, data)
        else:
            response = self.opener.open(url)
        self.currently_at = response.geturl()
        if response.info().get('Content-Encoding') == 'gzip':
            return unzip(response.read())
        else:
            return response.read()

    def get_content(self, url, payload_data=None):
        bs = BeautifulSoup(self.get_url(url, payload_data))
        return BeautifulSoup(self.get_url(bs.find('frame', title='Main Content')['src']))

    def navigate_content(self, url, payload_data=None):
        return BeautifulSoup(self.get_url(url, payload_data))

    def get_nav_link_by_name(self, link):
        try:
            return self.site_tree.find('a', attrs={'name': link})['href']
        except TypeError:
            return None

    def get_nav_link_by_title(self, link):
        try:
            return self.site_tree.find('a', title=link)['href']
        except TypeError:
            return None

    def get_content_link_by_title(self, content, link):
        return content.find('a', title=link)['href']

    def submit_form(self, content, form_id=None, extra_data=None, force_url=None):
        payload = {}

        if form_id:
            form = content.find('form', id=form_id)
            hiddens = form.find_all('input', type='hidden')
        else:
            hiddens = content.find_all('input', type='hidden')

        for el in hiddens:
            payload[el.attrs['name']] = el['value']

        if extra_data:
            for data in extra_data.iteritems():
                payload[data[0]] = data[1]

        if force_url:
            url = force_url
        else:
            url = form['action']

        return self.navigate_content(url, payload)

    def in_section(self, section):
        if section == 'registration':
            return self.netloc == self.REGISTRATION_NETLOC

    @property
    def netloc(self):
        return urlparse.urlparse(self.currently_at)[1]

    def get_student_record(self):
        link = self.ACADEMIC_LINK
        content = self.get_content(self.get_nav_link_by_title(link))
        link = self.STUDENT_RECORD_LINK
        self.student_record = self.get_content(self.get_content_link_by_title(content, link))

    def parse_student_record(self, student):
        if not self.student_record:
            self.get_student_record()
        stud_rec = StudentRecord.objects.get(student=student)
        main_div = self.student_record.find('div', id='SIMSPrintSection')
        student_bs = main_div.table.tr.nextSibling
        stud_info = self.parse_student_info(student_bs)
        degree_req_bs = student_bs.nextSibling
        exemption_bs = degree_req_bs.nextSibling
        table_of_takens_bs = exemption_bs.nextSibling.table
        current_row = table_of_takens_bs.tr
        while current_row:
            current_text = current_row.get_text()
            if 'ACADEMIC YEAR' in current_text:
                self.current_year = current_text[14:18]
            elif 'SUMMER' in current_text or 'FALL-WINTER' in current_text:
                # we can ignore it
                pass
                #self.current_semester = Semester.objects.get(year=self.current_year, period=Semester.SUMMER_1)
            elif 'Grade/Notation/GPA' in current_text:
                pass
            else:
                current_text = gen_string_from_current_row(current_row)
                m = re.match(self.STUDENT_RECORD_REGEX, current_text)
                if m:
                    course_letters = m.group(1)
                    course_numbers = m.group(2)
                    semester = m.group(3)
                    sem = Semester.objects.get(year=self.current_year, period=SEMESTER_MAPPER[semester])
                    sec_name = m.group(4)
                    course_name = m.group(5)
                    course_credits = m.group(6)
                    grade_received = m.group(7)
                    notation = m.group(8)
                    gpa_received = m.group(9)
                    class_avg = m.group(10)
                    class_size = m.group(11)
                    credits_received = m.group(12)
                    other = m.group(13)

                    course = Course.objects.get(course_letters=course_letters, course_numbers=course_numbers)
                    try:
                        sec = Section.objects.get(course=course, semester_year=sem, name=sec_name)
                    except Section.DoesNotExist:
                        sec = Section(course=course, semester_year=sem, name=sec_name, sec_type=Section.LECTURE,
                                      days='')
                        sec.save()

                    try:
                        rec_ent = StudentRecordEntry.objects.get(student_record=stud_rec, section=sec)
                    except StudentRecordEntry.DoesNotExist:
                        rec_ent = StudentRecordEntry(student_record=stud_rec, section=sec)

                    if self.current_year < '2013' and gpa_received is not None:
                        rec_ent.state = StudentRecordEntry.COMPLETED
                        rec_ent.result_grade = gpa_received
                    else:
                        rec_ent.state = StudentRecordEntry.REGISTERED

                    rec_ent.result_grade = gpa_received
                    rec_ent.save()

                print gen_string_from_current_row(current_row)
            current_row = current_row.nextSibling
        return stud_info, stud_rec.studentrecordentry_set.all()
        #return table_blah

    def parse_student_info(self, bs):
        id_row = bs.table.tr
        id_num = id_row.td.b.get_text()
        name_row = id_row.nextSibling
        first_name, last_name = name_row.td.get_text().split(u'\xa0')
        next_row = name_row.nextSibling
        next_row = next_row.nextSibling
        date_of_birth_text, sex = next_row.td.nextSibling.get_text().split(u'\xa0')
        import datetime
        dob = datetime.datetime.strptime(date_of_birth_text, '%d/%m/%y').date()
        stud_info = {
            'id': id_num,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob,
            'gender': sex.strip(),
        }
        return stud_info

    def goto_registration(self):
        link = 'Registration'
        content = self.get_content(self.get_nav_link_by_title(link))
        link = 'Undergraduate Registration'
        content = self.get_content(self.get_content_link_by_title(content, link))
        content = self.navigate_content(content.meta['content'][6:])
        form_id = 'form2'  # Continue
        self.current_bs = self.submit_form(content, form_id)

    def add_course(self, sec_info):
        if not self.in_section('registration'):
            self.goto_registration()
        form_id = 'form2'  # Add a Course
        content = self.submit_form(self.current_bs, form_id)
        #print content
        course_to_search = {
            'InputCourName': sec_info['course_letters'],
            'InputCourNum': sec_info['course_numbers'],
            'InputCourSes': '',
            'InputCourSec': '',
            'coursub': 'Submit',
            'selectoption': 'S'
        }
        content = self.submit_form(content, form_id, course_to_search, force_url='./wr220.asp')
        print content
        sessid = content.find('input', type='hidden', attrs={'name': 'Id'})['value']
        print sessid
        course_to_add = {
            'CourName': sec_info['course_letters'],
            'CourNo': sec_info['course_numbers'],
            'Sess': '4',
            'MainSec': sec_info['MainSec'],
            'RelSec1': sec_info['RelSec1'],
            'RelSec2': sec_info['RelSec2'],
            'CatNum': '12345',
            'Start': '1745',
            'Finish': '2015',
            'Days': '-------',
            'Campus': 'S',
            'Title': 'OPERATING SYSTEMS',
            'Id': sessid,
            'language': '1'
        }
        content = self.navigate_content('./wr225.asp', course_to_add)
        return content
        #content = self.submit_form(content, form_id)

    def get_user_status(self):
        status_link = self.get_nav_link_by_name('CU_ADDISPLAY')
        content = self.get_content(status_link)
        stud_access = content.find('li').get_text()
        student = False
        m = re.match('Undergraduate/Graduate Student Access enabled', stud_access)
        if m:
            student = True
        return student





def unzip(gzipped_data):
    buf = StringIO(gzipped_data)
    unzipped = gzip.GzipFile(fileobj=buf)
    return unzipped.read()

def gen_string_from_current_row(row):
    b = []
    for a in row.contents:
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