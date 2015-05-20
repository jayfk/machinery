# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.views.generic import TemplateView, FormView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from .models import CLOUD_DRIVER


class DriverMixin(object):
    """
    View mixin that adds some basic functions for views that handle drivers:

    - Adds the driver name and the logo to the context
    - Auto imports the correct driver class
    - Raises a Http404 for invalid drivers
    """

    def get_context_data(self, **kwargs):
        """
        Adds the driver name and the logo to the context
        """
        data = super(DriverMixin, self).get_context_data(**kwargs)
        model = self.get_model()
        data["driver_name"] = model.driver_name()
        data["logo"] = model.logo()
        return data

    def get_model(self):
        """
        Auto imports the driver model based on the `identifier` in kwargs
        """
        models_module = __import__("drivers.models", fromlist=[driver.identifier() for driver in CLOUD_DRIVER])
        return getattr(models_module, self.kwargs["identifier"])

    def dispatch(self, request, *args, **kwargs):
        """
        Makes sure that the driver exists, raises a Http404 otherwise
        """
        #make sure that only available drivers are accessed
        if self.kwargs["identifier"] not in [driver.identifier() for driver in CLOUD_DRIVER]:
            raise Http404
        return super(DriverMixin, self).dispatch(request, *args, **kwargs)


class DriverDeleteView(DriverMixin, DeleteView):
    """
    View that handles the deletion of a (Cloud)Driver instance
    """

    template_name = "drivers/delete.html"
    success_url = reverse_lazy("machines:driver")

    def get_object(self, queryset=None):
        return self.get_model().objects.get(pk=self.kwargs["pk"])


class DriverAddView(DriverMixin, FormView):
    """
    View that handles the creation of a new (Cloud)Driver
    """

    template_name = "drivers/add.html"

    success_url = reverse_lazy("machines:driver")

    def get_form_class(self):
        model = self.get_model()
        return model.form()

    def form_valid(self, form):
        obj = form.save()
        data = form.cleaned_data
        if data["edit_defaults"]:
            # redirect to the 'edit defaults' view if edit_defaults is True
            return HttpResponseRedirect(reverse("drivers:add_defaults", kwargs={"identifier": self.kwargs["identifier"]}))
        return HttpResponseRedirect(reverse("machines:add_cloud",
                                            kwargs={"identifier": self.kwargs["identifier"], "instance": obj.pk}))


class DriverAddDefaultsView(DriverMixin, FormView):
    """
    View that handles the creation of a default settings model.

    Please note: Save functionality not yet implemented, rather useless at this point.
    """

    template_name = "drivers/add.html"
    success_url = reverse_lazy("machines:driver")

    def get_form_class(self):
        model = self.get_model()
        return model.settings_form()


class DriverListView(TemplateView):
    """
    View to display all available cloud drivers.
    """

    template_name = "drivers/list.html"

    def get_context_data(self, **kwargs):
        data = super(DriverListView, self).get_context_data(**kwargs)
        data["drivers"] = CLOUD_DRIVER
        return data