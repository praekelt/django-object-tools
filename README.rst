Django Object Tools
===================
**Django app enabling painless creation of additional admin object tools by third party apps.**

.. contents:: Contents
    :depth: 5

This packages is part of the larger `Jmbo <http://www.jmbo.org>`_ project.

Installation
------------
#. Install or add ``django-object-tools`` to your python path.

#. Add ``object_tools`` to your ``INSTALLED_APPS`` setting. ``django-object-tools`` overrides some admin templates so you have to add it **before** ``django.contrib.admin``.

#. Hook up URLConf. Do this by pointing a given URL at the ``Tools.urls`` method. In this example, we register the default ``Tools`` instance ``object_tools.tools`` at the URL ``/object-tools/``::
    
    # urls.py
    from django.conf.urls.defaults import *

    import object_tools

    object_tools.autodiscover()

    urlpatterns = patterns('',
        (r'^object-tools/', include(object_tools.tools.urls)),
    )

#. Obviously Django Admin itself needs to be installed, as described `here <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

Usage
-----

``django-object-tools`` itself doesn't do much in terms of providing useful object tools. Its purpose is to simplify creation and integration of custom tools delivered by other Django applications. To that end it takes care of the messy details like permissions and admin template integration so you can focus on the fun stuff.

As an example lets create a tool allowing you to delete all objects. Yes this is a bit convoluted but it's a good toy example for illustration purposes. Have a look at `django-export <http://pypi.python.org/pypi/django-export>`_ and `django-order <http://pypi.python.org/pypi/django-order>`_ for examples of real world tools leveraging ``django-object-tools``.    

Firstly create a Django app folder structure as per usual, with the root directory named ``delete``, including a file called ``tools.py``. It should look as follows::

    delete/
        __init__.py
        tools.py

Edit tools.py to look like this::

    import object_tools

    from django.contrib.admin.actions import delete_selected

    class Delete(object_tools.ObjectTool):
        name = 'delete'
        label = 'Delete All'

        def view(self, request, extra_context=None):
            queryset = self.model.objects.all()
            response = delete_selected(self.modeladmin, request, queryset)
            if response:
                return response
            else:
                return self.modeladmin.changelist_view(request)

    object_tools.tools.register(Delete)


    
