from django.conf.urls import patterns, url

from profiles import views

urlpatterns = patterns('',
    url(r'^$', views.profile, name='profile'),
    url(r'^conflicts/$', views.conflicts, name='conflicts'),
    url(r'^admin/spaces/$', views.spaces, name='spaces'),
    url(r'^admin/members/$', views.members, name='members')
)