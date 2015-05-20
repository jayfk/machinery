#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "machinery.settings")

    from django.core.management import execute_from_command_line
    import Cookie
    import machines.urls
    import drivers.urls
    import preferences.urls

    import machinery.settings

    from django.utils import six
    import HTMLParser
    import django.contrib.admin
    import django.contrib.admin.apps
    import django.contrib.auth.apps
    import django.contrib.contenttypes.apps
    import django.contrib.sessions.apps
    import django.contrib.messages.apps
    import django.contrib.staticfiles.apps

    #import materialize
    #import materializecssform
    import crispy_forms
    import crispy_forms_materialize
    import drivers
    import machines
    import preferences

    import django.core.urlresolvers
    import machinery.urls
    import drivers.urls
    import preferences.urls
    #import django.contrib.admin.management.commands.runserver
    import django.core.management.commands.runserver
    import django.contrib.staticfiles.management.commands.runserver
    import django.contrib.sessions.serializers
    import django.templatetags.i18n
    import machines.context_processors
    import crispy_forms.templatetags.crispy_forms_field
    execute_from_command_line(sys.argv)