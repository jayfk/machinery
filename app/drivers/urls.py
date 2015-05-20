# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add/(?P<identifier>[\w]+)/$', views.DriverAddView.as_view(), name="add"),
    url(r'^delete/(?P<identifier>[\w]+)/(?P<pk>\d+)$', views.DriverDeleteView.as_view(), name="delete"),
    url(r'^add-defaults/(?P<identifier>[\w]+)/$', views.DriverAddDefaultsView.as_view(), name="add_defaults"),
    url(r'^list/', views.DriverListView.as_view(), name="list"),
]