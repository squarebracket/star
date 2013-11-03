from django.conf.urls import patterns, url

from scheduler import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),

    url(r'^schedule', views.schedule, name='schedule'),
    url(r'^add_course', views.add_course, name='add_course'),
    url(r'^register', views.register, name='register'),
    url(r'^drop', views.drop, name='drop'),

)
