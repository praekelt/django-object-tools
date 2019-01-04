import django
import object_tools
from django.contrib import admin

if django.VERSION >= (2, 0):
    from django.urls import path

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('object-tools/', object_tools.tools.urls),
    ]
else:
    try:
        from django.conf.urls.defaults import include, url
    except ImportError:
        from django.conf.urls import include, url

    admin.autodiscover()
    object_tools.autodiscover()

    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^object-tools/', include(object_tools.tools.urls)),
    ]
