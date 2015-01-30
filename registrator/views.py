# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from scheduler.models.schedule_generator import *
from uni_info.models import Course, Semester
from registrator.models import StudentRecord
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


@login_required
def student_record(request):
    student_record = StudentRecord.objects.get(student=request.user.student)
    return render_to_response('registrator/student_record.html', {'student_record': student_record})


def register_for_section(request, section=None):
    if section:
        backend = request.session['reg']
        backend.register_for_course(section)