from django.conf.urls import patterns, url

from scheduler import views

urlpatterns = patterns('',

    url(r'^search', views.search, name='search'),
    url(r'^schedule', views.schedule, name='schedule'),
    url(r'^add_course', views.add_course, name='add_course'),
    url(r'^register', views.register, name='register'),
    url(r'^drop', views.drop, name='drop'),
    url(r'search_for_course_by_name_and_semester',views.search_for_course_by_name_and_semester, name='search_for_course_by_name_and_semester'),
)
