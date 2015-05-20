# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.urlresolvers import reverse
from .core import machines_ls


def machine_cache_context_processor(request):
    """
    Basic context processor to populate the context with a cached list of machines.
    """
    return {"machines": machines_ls(cached=True),
            "sidebar_url": reverse("machines:list-sidebar-partial")}