from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from scheduler.models import AcademicProgram, Course, AcademicRequirement, \
    StudentRecordEntry, StudentRecord, Student, Section, ScheduleItem, \
    Registration, Professor, Corequisite, Prerequisite, Director, Registrar,\
    Lab, Tutorial, Lecture, AcademicInstitution, Faculty, Building, Facility, Semester

admin.site.register(AcademicInstitution)
admin.site.register(Faculty)
admin.site.register(AcademicProgram)
admin.site.register(Course)
admin.site.register(AcademicRequirement)
admin.site.register(Semester)
admin.site.register(Section)
admin.site.register(Building)
admin.site.register(Facility)
admin.site.register(ScheduleItem)
admin.site.register(Student)
admin.site.register(StudentRecord)
admin.site.register(StudentRecordEntry)
admin.site.register(Registration)
admin.site.register(Professor)
admin.site.register(Registrar)
admin.site.register(Director)
admin.site.register(Prerequisite)
admin.site.register(Corequisite)
admin.site.register(Lab)
admin.site.register(Tutorial)
admin.site.register(Lecture)


admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    url(r'^$', 'scheduler.views.index', name='home'),

    url(r'^scheduler/', include('scheduler.urls', namespace="scheduler")),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
