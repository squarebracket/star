from django.conf.urls import patterns, url

from scheduler import views

urlpatterns = patterns('',

                       url(r'^find', views.find, name='find'),
                       url(r'^schedule', views.schedule, name='schedule'),
                       url(r'^stream_schedule', views.stream_schedule, name='stream_schedule'),
                       url(r'^add_course', views.add_course, name='add_course'),
                       url(r'^register', views.register, name='register'),
                       url(r'^drop', views.drop, name='drop'),
                       url(r'^remove_course', views.remove_course, name='remove_course'),
                       url(r'search_for_course_by_name_and_semester', views.search_for_course_by_name_and_semester,
                           name='search_for_course_by_name_and_semester'),
                       url(r'^section_permutation_by_course_name',views.section_permutation_by_course_name,
                           name='section_permutation_by_course_name')
)
