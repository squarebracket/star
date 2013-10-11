from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext


def index(request):
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
        'student': request.user,
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