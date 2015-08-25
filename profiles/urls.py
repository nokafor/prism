from django.conf.urls import patterns, url

from profiles import views

urlpatterns = patterns('',
    url(r'^$', views.profile, name='profile'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^conflicts/$', views.conflicts, name='conflicts'),
    url(r'^conflicts/add/(?P<date_string>[\w|\W\-\d\%]+)/$', views.testing, name='testing'),
    url(r'^casts/$', views.casts, name='casts'),
    url(r'^spaces/$', views.spaces, name='spaces'),
    url(r'^spaces/parsePAC$', views.parsePAC, name='parsePAC'),
    url(r'^members/$', views.members, name='members'),
    url(r'^admin/scheduling/$', views.scheduling, name='scheduling'),
    url(r'^admin/addUsers/$', views.addUsers, name='addUsers'),
    url(r'^due_dates/(?P<option>[\w|\W]+)/$', views.updateDueDate, name='updateDueDate')
)