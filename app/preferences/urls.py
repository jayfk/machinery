# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^/$', views.SettingsEditView.as_view(), name="edit"),
]