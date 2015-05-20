from django.views.generic import TemplateView


class SettingsEditView(TemplateView):

    template_name = "settings/edit.html"
