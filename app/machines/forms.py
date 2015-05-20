# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django import forms
from .models import Job
from crispy_forms.helper import FormHelper
from .core import machines_ls


class JobForm(forms.Form):

    job = forms.ModelChoiceField(queryset=Job.objects.all())


class MachineDeleteForm(forms.Form):

    name = forms.CharField(max_length=40)


class MachineForm(forms.Form):

    name = forms.CharField(max_length=40, help_text="Unique Name for your machine")
    enable_swarm = forms.BooleanField(initial=False, required=False, help_text="Configure Machine with Swarm")

    def __init__(self, *args, **kwargs):
        super(MachineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_name(self):
        """
        checks if a machine with this name already exists and raises an ValidationError if this is the case
        """
        name = self.cleaned_data["name"]
        machines = machines_ls(cached=True)
        if machines is not None:
            for machine in machines:
                if machine["name"] == name:
                    raise forms.ValidationError("A machine with the name {0} already exists".format(name))
        return name


class SwarmForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SwarmForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    swarm_discovery = forms.CharField(max_length=100, required=False, help_text="Discovery service to use with Swarm")
    swarm_master = forms.BooleanField(initial=False, required=False, help_text="Configure Machine to be a Swarm master")
    swarm_host = forms.CharField(max_length=70, required=False, help_text="ip/socket to listen on for Swarm master")
    swarm_addr = forms.CharField(max_length=70, required=False,
                                 help_text="addr to advertise for Swarm (default: detect and use the machine IP)")