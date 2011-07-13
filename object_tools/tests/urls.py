from django.conf.urls.defaults import *

import object_tools
object_tools.autodiscover()

urlpatterns = patterns('',
    (r'^object-tools/', include(object_tools.tools.urls)),
)
