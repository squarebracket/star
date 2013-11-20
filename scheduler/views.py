from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from scheduler.models.schedule_generator import *
from uni_info.models import Course, Semester
import json
import re


@login_required
def register(request):
    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem for sem in Semester.objects.all() if sem.is_open]
    })

    return render(request, 'scheduler/register.html', context)

@login_required
def do_register(request):
    """
    Registers a course for a student by name for semester by name
    """
    course_name = request.POST['course_name'].upper()
    semester_name = request.POST['semester_name']
    request_student = request.user.student
    try:
        #find course by name
        course = Course.objects.get(name=course_name)
        #find semester by name
        semester = [sem for sem in Semester.objects.all() if sem.name == semester_name][0]
        #register for the course for semester
        request_student.register_for_course(course, semester)

        #Load error and info into request messages and then clear lists
        for error in request_student.error_list:
            messages.error(request, error)
        request_student.clear_error_list()

        for info in request_student.info_list:
            messages.info(request, info)
        request_student.clear_info_list()
    except Course.DoesNotExist:
        #error, course not found
        messages.error(request, "course not found")

    return HttpResponseRedirect(reverse('scheduler:student'))


@login_required
def drop(request):
    """
    Drops a course for a student by name
    """
    course_name = request.GET['course_name']
    for_student = request.user.student
    course = Course.objects.get(name=course_name)

    for_student.drop_course(course)
    return HttpResponseRedirect(reverse('scheduler:student'))


def find(request):
    if request.session.get('course_list', False):
        pass
    else:
        request.session['course_list'] = []

    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem for sem in Semester.objects.all() if sem.is_open],
        'course_list': request.session['course_list']
    })

    return render(request, 'scheduler/find.html', context)


@login_required
def generate_schedule(request):
    """
    """
    courses = request.session.get('course_list')
    semester = Semester.objects.get(year=2013, period=Semester.FALL)
    gen_r = ScheduleGenerator(courses, semester)
    schedules = gen_r.generate_schedules()
    request.session['schedule'] = schedules
    count = len(schedules)
    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem for sem in Semester.objects.all() if sem.is_open],
        'schedule_count': range(count)
    })

    return render(request, 'scheduler/schedule.html', context)


@login_required
def schedule(request):
    """
    Gets the current schedule
    """
    count = 0
    if request.session.get('schedule', False):
        count = len(request.session['schedule'])

    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem for sem in Semester.objects.all() if sem.is_open],
        'schedule_count': range(count)
    })
    return render(request, 'scheduler/schedule.html', context)


@login_required
def stream_schedule(request):
    """
    Stream the schedule
    """
    #stream_result = []
    #
    #a = {'id': 1,
    #     'title': 'SOEN 341',
    #     'allDay': False,
    #     'start': 'Mon, 18 Nov 2013 13:00:00 EST',
    #     'end': 'Mon, 18 Nov 2013 14:00:00 EST'
    #     }
    #b = {'id': 2,
    #     'title': 'SOEN 341',
    #     'allDay': False,
    #     'start': 'Wed, 20 Nov 2013 12:00:00 EST',
    #     'end': 'Wed, 20 Nov 2013 14:00:00 EST',
    #    }
    #c = {'id': 3,
    #     'title': 'SOEN 341',
    #     'allDay': False,
    #     'start': 'Fri, 22 Nov 2013 11:00:00 EST',
    #     'end': 'Fri, 22 Nov 2013 15:00:00 EST'
    #     }
    #
    #stream_result.append(a)
    #stream_result.append(b)
    #stream_result.append(c)
    #stream_json_result = json.dumps(stream_result)
    #stream_json_result = '[{"start": "Wed, 20 Nov 2013 11:45:00 EST", "allDay": false, "end": "Wed, 20 Nov 2013 13:00:00 EST", "id": "840_W", "title": "ENGR213: 1 U/Fall 2013"}, {"start": "Fri, 22 Nov 2013 11:45:00 EST", "allDay": false, "end": "Fri, 22 Nov 2013 13:00:00 EST", "id": "840_F", "title": "ENGR213: 1 U/Fall 2013"}, {"start": "Fri, 22 Nov 2013 14:15:00 EST", "allDay": false, "end": "Fri, 22 Nov 2013 15:55:00 EST", "id": "841_F", "title": "ENGR213: 2 UA/Fall 2013"}, {"start": "Tue, 19 Nov 2013 10:15:00 EST", "allDay": false, "end": "Tue, 19 Nov 2013 11:30:00 EST", "id": "904_T", "title": "ENGR242: 1 X/Fall 2013"}, {"start": "Thu, 21 Nov 2013 10:15:00 EST", "allDay": false, "end": "Thu, 21 Nov 2013 11:30:00 EST", "id": "904_J", "title": "ENGR242: 1 X/Fall 2013"}, {"start": "Thu, 21 Nov 2013 17:45:00 EST", "allDay": false, "end": "Thu, 21 Nov 2013 19:25:00 EST", "id": "905_J", "title": "ENGR242: 2 XA/Fall 2013"}, {"start": "Tue, 19 Nov 2013 08:45:00 EST", "allDay": false, "end": "Tue, 19 Nov 2013 10:00:00 EST", "id": "1592_T", "title": "MECH215: 1 T/Fall 2013"}, {"start": "Thu, 21 Nov 2013 08:45:00 EST", "allDay": false, "end": "Thu, 21 Nov 2013 10:00:00 EST", "id": "1592_J", "title": "MECH215: 1 T/Fall 2013"}, {"start": "Thu, 21 Nov 2013 16:15:00 EST", "allDay": false, "end": "Thu, 21 Nov 2013 17:05:00 EST", "id": "1593_J", "title": "MECH215: 2 TA/Fall 2013"}, {"start": "Tue, 19 Nov 2013 17:15:00 EST", "allDay": false, "end": "Tue, 19 Nov 2013 18:05:00 EST", "id": "1594_T", "title": "MECH215: 3 TI/Fall 2013"}]'
    schedule_index = request.GET['index']
    schedules = request.session['schedule']
    index = int(schedule_index)
    schedule_result = schedules[index]
    stream_json_result = schedule_result.schedule_json()

    return HttpResponse(stream_json_result, content_type="application/json")


@login_required
def add_course(request):
    """
    Adds a course to a schedule stored in an authenticated users' session
    """
    course_search = request.POST['course_name']
    semester_id = request.POST['semester_id']
    request_student = request.user.student

    try:
        #find course(s) matching query
        results = Course.full_search(course_search)
        if len(results) == 1:
            course = results[0]
        else:
            messages.error(request, "multiple courses found")
        #find semester by name
        #semester = [sem for sem in Semester.objects.all() if sem.id == semester_id][0]

        course_list = request.session['course_list']
        course_list.append(course)
        request.session['course_list'] = course_list

    except Course.DoesNotExist:
        #error, no courses found
        messages.error(request, "course not found")

    return HttpResponseRedirect(reverse('scheduler:find'))

@login_required
def remove_course(request):

    course_name = request.GET['course_name'].upper()
    course_list = request.session['course_list']
    found_to_delete = None
    for course in course_list:
        if course.name == course_name:
            found_to_delete = course

    if found_to_delete is not None:
        course_list.remove(found_to_delete)

    request.session['course_list'] = course_list

    return HttpResponseRedirect(reverse('scheduler:find'))


def search_for_course_by_name_and_semester(request):
    """
    Uses course_name and semester_list of request to return a list of courses

    Method that accepts a request and then extracts the parameters of course _name_search and semester_list
    Using those 2 parameters, accesses Django Course.objects and filter the ones that match by wild card the name.
    Further reduces this list by checking that they are offered in at least one of the semesters in the semester_list.
    """
    #find course by name
    course_name = request.GET['term'].upper()
    #semester list
    semester_id_list = request.GET.getlist('semester_id')
    search_regex = r'' + course_name
    result = Course.full_search(search_regex)

    offered_courses = []

    for course in result:
        for semester_id in semester_id_list:
            if course.section_set.filter(semester_year=semester_id).count() > 0:
                offered_courses.append(course)
                break

    result_list = []
    for course in offered_courses:
        entry = {"label": str(course), "desc": course.name}
        result_list.append(entry)

    json_result = json.dumps(result_list)
    return HttpResponse(json_result, content_type="application/json")


def section_permutation_by_course_name(request):
    #Method that accepts a request and then extracts the parameters of course_name and semester_list.
    #Use Django Course.objects to find the course and then find all the sections for all the semesters in semester_list.
    #Now generate all the valid and non conflicting Lecture/Lab/Tutorial combination, serialize result into JSON and return request.
    #The resulting combined object's JSON data should contain a unique identifier created by the sections so that it can be passed back to the server to specify if it is to be included in schedule generation.


    #find course by name
    course_name = request.GET['course_name'].upper()
    #semester list
    semester_id = request.GET.getlist('semester_id')

    search_regex = r'' + course_name
    result = Course.search_by_regex(search_regex)
    course_list = []
    id_list = []

    #convert queryset to list
    for course in result:
        course_list.append(course.name)

    #convert queryset to list
    for semester in semester_id:
        id_list.append(semester)

    sections_by_semester = []
    for course in result:
        for id in id_list:
            sections_by_semester.extend(course.get_sections_for_semester(id))

    permutation_list = []

    for section in sections_by_semester:
        permutation_list.append(get_section_permutations(section))

    result_list = []
    json_result = []
    return HttpResponse(json_result, content_type="application/json")
