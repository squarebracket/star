from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from uni_info.models import Course, Semester
import json


@login_required
def register(request):
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


@login_required
def schedule(request):
    """
    Gets the current schedule
    """

    if request.session.get('schedule', False):
        pass
    else:
        reg_schedule = request.user.student.create_schedule_from_registered_courses()
        request.session['schedule'] = reg_schedule

    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem for sem in Semester.objects.all() if sem.is_open],
        'schedule': request.session['schedule']
    })
    return render(request, 'scheduler/schedule.html', context)


@login_required
def add_course(request):
    """
    Registers a course for a student by name for semester by name
    """
    course_name = request.POST['course_name'].upper()
    semester_name = request.POST['semester_name']
    request_schedule = request.session['schedule']
    request_student = request.user.student

    try:
        #find course by name
        course = Course.objects.get(name=course_name)
        #find semester by name
        semester = [sem for sem in Semester.objects.all() if sem.name == semester_name][0]

        new_schedule = request_student.add_to_schedule(request_schedule, course, semester)
        request.session['schedule'] = new_schedule

    except Course.DoesNotExist:
        #error, course not found
        messages.error(request, "course not found")

    return HttpResponseRedirect(reverse('scheduler:schedule'))


def search_for_course_by_name_and_semester(request):
    """
    Method that accepts a request and then extracts the parameters of course _name_search and semester_list
    Using those 2 parameters, accesses Django Course.objects and filter the ones that match by wild card the name.
    Further reduces this list by checking that they are offered in at least one of the semesters in the semester_list.
    """
    #find course by name
    course_name = request.GET['course_name'].upper()
    #semester list
    semester_id = request.GET.getlist('semester_id')
    search_regex = r'' + course_name
    result = Course.search_by_regex(search_regex)
    course_list = []

    #convert queryset to list
    for course in result:
        course_list.append(course.name)

    #convert queryset to list
    id_list = []
    for semester in semester_id:
        id_list.append(semester)

    sections_by_semester = []

    for course in result:
        for id in id_list:
            sections_by_semester.extend(course.get_sections_for_semester(id))

    result_list = []
    for s in sections_by_semester:
        entry = {'label': s.course.name, 'desc': s.course.description}
        result_list.append(entry)

    json_result = json.dumps(result_list)
    return HttpResponse(json_result, content_type="application/json")
