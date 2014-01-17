# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from scheduler.models.schedule_generator import *
from uni_info.models import Course, Semester
from registrator.models import RegistrationProxy
import json
import re


@login_required
def register_for_schedule(request):
    schedule_index = request.GET['index']
    schedules = request.session['schedule']
    index = int(schedule_index) - 1
    schedule_result = schedules[index]
    for item in schedule_result.schedule_items:
        reg = RegistrationProxy(user=request.user)
        reg.add_schedule_item(item)