# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^driver/$', views.MachineDriverView.as_view(), name="driver"),
    url(r'^list/$', views.MachineListView.as_view(), name="list"),

    url(r'^inspect/(?P<name>.*)/$', views.MachineInspectView.as_view(), name="inspect"),
    url(r'^inspect/(?P<name>.*)/partial/inspect$', views.MachineInspectPartialView.as_view(), name="inspect-partial"),

    url(r'^remove/(?P<name>.*)/$', views.MachineDeleteView.as_view(), name="remove"),

    url(r'^list/partial/sidebar$', views.MachinesSidebarPartialView.as_view(), name="list-sidebar-partial"),
    url(r'^list/partial/table$', views.MachinesListPartialView.as_view(), name="list-table-partial"),

    url(r'^add/local/(?P<identifier>[\w]+)/$', views.machine_add_view,
        kwargs={"driver": "local"}, name="add_local"),
    url(r'^add/cloud/(?P<identifier>[\w]+)/(?P<instance>[\d]+)/$', views.machine_add_view,
        kwargs={"driver": "cloud"}, name="add_cloud"),


    url(r'^job/(?P<pk>[\d]+)/$', views.JobView.as_view(), name="job"),
    url(r'^job/(?P<pk>[\d]+)/json$', views.JobProgressPartialView.as_view(), name="job-progress-partial"),
    url(r'^job/run$', views.JobLaunchView.as_view(), name="job-launch"),
    url(r'^job/(?P<pk>[\d]+)/error/$', views.JobErrorView.as_view(), name="job-error"),

]