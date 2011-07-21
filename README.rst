Django Object Tools
===================
**Django app enabling painless creation of additional admin object tools by third party apps.**

.. contents:: Contents
    :depth: 5

This packages is part of the larger `Jmbo <http://www.jmbo.org>`_ project.

Installation
------------

#. Install or add django-object-tools to your python path.

#. Add ``object_tools`` to your INSTALLED_APPS setting.

#. Hook up URLConf. Do this by pointing a given URL at the Tools.urls method. In this example, we register the default ``Tools`` instance ``object_tools.tools`` at the URL ``/object-tools/``::
    
    # urls.py
    from django.conf.urls.defaults import *

    import object_tools

    object_tools.autodiscover()

    urlpatterns = patterns('',
        (r'^object-tools/', include(object_tools.tools.urls)),
    )

