from django.conf.urls import include, url
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^machines/', include("machines.urls", namespace="machines")),
    url(r'^drivers/', include("drivers.urls", namespace="drivers")),
    url(r'^settings/', include("preferences.urls", namespace="settings")),
    url(r'^$', RedirectView.as_view(url="/machines/list/"), name="home"),
]
