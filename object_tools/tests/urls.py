import django
import object_tools
from django.contrib import admin

from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('object-tools/', object_tools.tools.urls),
]
    admin.autodiscover()
    object_tools.autodiscover()

    urlpatterns = [
        path('admin/', include(admin.site.urls)),
        path('object-tools/', include(object_tools.tools.urls)),
    ]
