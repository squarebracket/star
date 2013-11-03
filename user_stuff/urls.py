from django.conf.urls import patterns, url

from user_stuff import views

urlpatterns = patterns('',

    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),

    url(r'^student', views.student, name='student'),

)