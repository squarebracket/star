from django.conf.urls import patterns, url

from scheduler import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),

    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),

    url(r'^student', views.student, name='student'),
    url(r'^schedule', views.schedule, name='schedule'),
    url(r'^register', views.register, name='register'),
    url(r'^drop', views.drop, name='drop'),

)
