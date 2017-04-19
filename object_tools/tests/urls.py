try:
    from django.conf.urls.defaults import include, url
except ImportError:
    from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import object_tools
object_tools.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^object-tools/', include(object_tools.tools.urls)),
]
