from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from scheduler.models import Course, Semester


def index(request):
    """
    The main front page, allowing login of the user
    """
    context = RequestContext(request, {
        'welcome': 'welcome',
    })
    return render(request, 'scheduler/index.html', context)


@login_required
def student(request):
    """
    Show the main student page
    """
    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem.name for sem in Semester.objects.all() if sem.is_open],
    })
    return render(request, 'scheduler/student.html', context)


def login(request):
    """
    Login, takes username and password from request and authenticates user
    if user is valid, send to corresponding page, otherwise send to index
    """
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth_login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('scheduler:student'))
        else:
            # Return a 'disabled account' error message
            return HttpResponseRedirect(reverse('scheduler:index'))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('scheduler:index'))


def logout(request):
    """
    Logout, takes user out of session
    """
    auth_logout(request)
    return HttpResponseRedirect(reverse('scheduler:index'))


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
        'open_semesters': [sem.name for sem in Semester.objects.all() if sem.is_open],
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

        request_student.add_to_schedue(request_schedule, course, semester)
    except Course.DoesNotExist:
        #error, course not found
        messages.error(request, "course not found")

    return HttpResponseRedirect(reverse('scheduler:schedule'))