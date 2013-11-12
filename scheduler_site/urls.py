from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from registrator.models import StudentRecord, StudentRecordEntry
from uni_info.models import AcademicInstitution, Faculty, AcademicProgram, Course, AcademicRequirement, Semester, Section, Building, Facility
from user_stuff.models import Student, Professor, Director

admin.site.register(AcademicInstitution)
admin.site.register(Faculty)
admin.site.register(AcademicProgram)
admin.site.register(Course)
admin.site.register(AcademicRequirement)
admin.site.register(Semester)
admin.site.register(Section)
admin.site.register(Building)
admin.site.register(Facility)
admin.site.register(Student)
admin.site.register(StudentRecord)
admin.site.register(StudentRecordEntry)
admin.site.register(Professor)
admin.site.register(Director)


admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    url(r'^$', 'user_stuff.views.index', name='home'),

    url(r'^user_stuff/', include('user_stuff.urls', namespace="user_stuff")),
    url(r'^scheduler/', include('scheduler.urls', namespace="scheduler")),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
