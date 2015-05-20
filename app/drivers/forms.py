# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django import forms
from crispy_forms.helper import FormHelper


class DriverForm(forms.ModelForm):
    """
    Default Form for all cloud drivers.
    """

    # hide the edit defaults checkbox for now and set it to false until a proper default settings save implementation
    # is ready.
    edit_defaults = forms.BooleanField(initial=False, required=False, )

    def __init__(self, *args, **kwargs):
        super(DriverForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['edit_defaults'].widget = forms.HiddenInput()

    class Meta:
        exclude = ["settings"]


class SettingsForm(forms.ModelForm):
    """
    Default Form for all driver settings
    """

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


    @property
    def has_fields(self):
        """
        Returns `True` if the form has at least one field.
        :return: Bool
        """
        return self.fields != {}


# class AWSForm(DriverForm):
#    pass

# class AWSSettingsForm(SettingsForm):
#    pass

class OpenstackSettingsForm(SettingsForm):

    def clean(self):

        data = self.cleaned_data

        if not data["openstack_flavor_id"] and not data["openstack_flavor_name"]:
            raise forms.ValidationError("Flavor: Add ID or Name")

        if data["openstack_flavor_id"] and data["openstack_flavor_name"]:
            raise forms.ValidationError("Flavor: ID or Name, not both")

        if not data["openstack_image_id"] and not data["openstack_image_name"]:
            raise forms.ValidationError("Image: Add ID or Name")

        if data["openstack_image_id"] and data["openstack_image_name"]:
            raise forms.ValidationError("Image: ID or Name, not both")

        if not data["openstack_tenant_name"] and not data["openstack_tenant_id"]:
            raise forms.ValidationError("Tenant: Add ID or Name")

        if data["openstack_tenant_name"] and data["openstack_tenant_id"]:
            raise forms.ValidationError("Tenant: ID or Name, not both")

        #if not data["openstack_net_id"] and not data["openstack_net_name"]:
        #    raise forms.ValidationError("Net: Add ID or Name")

        #if data["openstack_net_id"] and data["openstack_net_name"]:
        #    raise forms.ValidationError("Net: ID or Name, not both")