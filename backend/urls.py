"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from backend.libs import handler_views
from backend.apps.sample import views as sample_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^datetime/?$', 'backend.apps.sample.views.datetime'),
    url(r'^datetime/?$', sample_views.datetime),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'jsonp'])
urlpatterns += staticfiles_urlpatterns()

handler400 = handler_views.handler400
handler404 = handler_views.handler404
handler500 = handler_views.handler500
