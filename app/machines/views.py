# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.views.generic import TemplateView, FormView, DetailView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.forms import Form
from django.contrib import messages

from drivers.models import CLOUD_DRIVER, LOCAL_DRIVER

from .core import machines_ls, machine_rm, get_machine_details
from .forms import MachineForm, SwarmForm, JobForm
from .models import Job


class MachineListView(TemplateView):
    """
    View to list all machines.
    """

    template_name = "machines/list.html"

    def get_context_data(self, **kwargs):
        data = super(MachineListView, self).get_context_data(**kwargs)
        data["table_url"] = reverse("machines:list-table-partial")
        return data


class MachineInspectView(TemplateView):
    """
    View to get details for a machine.
    """

    template_name = "machines/inspect.html"

    def get_context_data(self, **kwargs):
        data = super(MachineInspectView, self).get_context_data(**kwargs)
        data["machine"] = get_machine_details(self.kwargs["name"], cached=True)
        data["machine_name"] = self.kwargs["name"]
        if data["machine"] is not None:
            data["machine_driver"] = data["machine"]["inspect"].pop("Driver")
            data["machine_host_opts"] = data["machine"]["inspect"].pop("HostOptions")
        data["inspect_url"] = reverse("machines:inspect-partial", kwargs={"name": self.kwargs["name"]})
        return data


class MachineDriverView(TemplateView):
    """
    View to list all saved cloud driver instances and local drivers.
    """

    template_name = "machines/driver.html"

    def get_context_data(self, **kwargs):
        data = super(MachineDriverView, self).get_context_data(**kwargs)
        # This piece looks a bit complicated. All it does is to call objects.all() on every model in CLOUD DRIVER.
        # Since this returns a Queryset, the queryset gets evaluated using list(). The sublist is then flattened to get
        # a list of instances
        data["cloud_drivers"] = [item for sublist in [list(driver.objects.all()) for driver in CLOUD_DRIVER] for item in sublist]
        data["local_drivers"] = LOCAL_DRIVER
        return data


def machine_add_view(request, driver, identifier, instance=None):
    """
    View to add a new machine.

    Adds 3 forms to the context:

    - settings form
    - machine form
    - swarm form

    If all three forms a valid, a Job object is created and the view redirects to a URL that holds all information
    about the job and runs it (as a ajax request).

    :param request: django request object
    :param driver: str driver type (cloud or local)
    :param identifier: str driver identifier
    :param instance: cloud driver instance or None if local driver
    """

    if driver == "cloud":
        models_module = __import__("drivers.models", fromlist=[driver.identifier() for driver in CLOUD_DRIVER])
        if instance is None:
            raise Http404
    elif driver == "local":
        models_module = __import__("drivers.models", fromlist=[driver.identifier() for driver in LOCAL_DRIVER])
    else:
        # todo raise sth else here
        raise Http404

    model = getattr(models_module, identifier)

    driver_instance = get_object_or_404(model, pk=instance) if instance is not None else None

    settings_form_class = model.settings_form()
    machine_form_class = MachineForm
    swarm_form_class = SwarmForm

    if request.method == "POST":
        settings_form = settings_form_class(request.POST, prefix="settings")
        machine_form = machine_form_class(request.POST, prefix="machine")
        swarm_form = swarm_form_class(request.POST, prefix="swarm")

        if settings_form.is_valid() and machine_form.is_valid() and swarm_form.is_valid():
            driver_dict = driver_instance.as_dict if driver_instance is not None else {"driver": model.Properties.driver}
            params = {
                "name": machine_form.cleaned_data["name"],
                "swarm": swarm_form.cleaned_data,
                "driver": driver_dict,
                "settings": settings_form.cleaned_data,
            }
            #cli_command = create_params(name=machine_form.cleaned_data["name"], swarm_dict=swarm_form.cleaned_data,
            #                            driver_dict=driver_dict, settings_dict=settings_form.cleaned_data)
            job = Job.objects.create(params=params, name=machine_form.cleaned_data["name"])
            return HttpResponseRedirect(reverse("machines:job", kwargs={"pk": job.pk}))

    else:

        swarm_form = swarm_form_class(prefix="swarm")
        settings_form = settings_form_class(prefix="settings")
        machine_form = machine_form_class(prefix="machine")

    return render(request, 'machines/add.html', {"settings_form": settings_form, "machine_form": machine_form,
                                                 "swarm_form": swarm_form, "driver": model, "driver_instance": driver_instance})


class MachineDeleteView(FormView):
    """
    View to delete a machine.
    """

    form_class = Form
    success_url = reverse_lazy("home")
    template_name = "machines/remove.html"

    def form_valid(self, form):
        success, output = machine_rm(name=self.kwargs["name"])
        if not success:
            machine_rm(name=self.kwargs["name"], force=True)
            messages.add_message(self.request, messages.ERROR,
                                 'Error removing machine gracefully, had to use force. Log: {0}'.format(output))
        return super(MachineDeleteView, self).form_valid(form)


class JobView(DetailView):
    """
    View that holds all information about a Job.

    Adds 3 URLs to the context:

    - poll_url: URL to poll for new output from stdout.
    - launch_url: URL to launch the Job through a request.
    - redirect_url: URL to redirect to if the Job terminated successfully
    """

    template_name = "machines/job/job.html"
    model = Job
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        data = super(JobView, self).get_context_data(**kwargs)
        data["poll_url"] = reverse("machines:job-progress-partial", kwargs={"pk": self.kwargs["pk"]})
        data["launch_url"] = reverse("machines:job-launch")
        data["redirect_url"] = reverse("machines:inspect", kwargs={"name": self.object.name})
        return data


class JobErrorView(DetailView):
    """
    View that displays error information about a Job.
    """

    template_name = "machines/job/error.html"
    model = Job
    context_object_name = "job"


class JobProgressPartialView(DetailView):
    """
    View that returns the Jobs progress (output) as JSON
    """

    model = Job

    def render_to_response(self, context, **response_kwargs):
        data = {"content": render_to_string("machines/include/job.html", {"job": self.object})}
        return JsonResponse(data)


class JobLaunchView(FormView):
    """
    View that launches a Job.
    """

    model = Job
    form_class = JobForm

    def form_valid(self, form):
        job = form.cleaned_data["job"]
        return self.render_to_json_response(job=job)

    def render_to_json_response(self, job):
        data = {"success": job.run()}
        return JsonResponse(data)


class MachinesSidebarPartialView(TemplateView):
    """
    View that returns the sidebar content as JSON
    """

    def render_to_response(self, context, **response_kwargs):
        data = {"content": render_to_string("machines/include/sidebar.html", {"machines": machines_ls()})}
        return JsonResponse(data)


class MachinesListPartialView(TemplateView):
    """
    View that returns a list of machines as JSON
    """

    def render_to_response(self, context, **response_kwargs):
        data = {"content": render_to_string("machines/include/list.html", {"machines": machines_ls()})}
        return JsonResponse(data)


class MachineInspectPartialView(TemplateView):
    """
    View that returns machine details as JSON
    """

    def render_to_response(self, context, **response_kwargs):
        data = {}
        data["machine"] = get_machine_details(self.kwargs["name"])
        data["machine_name"] = self.kwargs["name"]
        if data["machine"] is not None:
            data["machine_driver"] = data["machine"]["inspect"].pop("Driver")
            data["machine_host_opts"] = data["machine"]["inspect"].pop("HostOptions")
        data = {"content": render_to_string("machines/include/inspect.html", data)}
        return JsonResponse(data)