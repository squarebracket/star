# Create your views here.

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from uni_info.models import Semester


def index(request):
    """
    The main front page, allowing login of the user
    """
    context = RequestContext(request, {
        'welcome': 'welcome',
    })
    return render(request, 'user_stuff/index.html', context)

# TODO: Can this made generic?
@login_required
def student(request):
    """
    Show the main student page
    """
    context = RequestContext(request, {
        'user': request.user,
        'open_semesters': [sem.name for sem in Semester.objects.all() if sem.is_open],
    })
    return render(request, 'user_stuff/student.html', context)


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
            return HttpResponseRedirect(reverse('user_stuff:student'))
        else:
            # Return a 'disabled account' error message
            return HttpResponseRedirect(reverse('user_stuff:index'))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('user_stuff:index'))


def logout(request):
    """
    Logout, takes user out of session
    """
    auth_logout(request)
    return HttpResponseRedirect(reverse('user_stuff:index'))

