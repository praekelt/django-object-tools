from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)


class ObjectTool(object):
    """
    Base class from which all other tools should inherit.
    Provides setup and utility method for easily rendering a form in admin.
    """
    def __init__(self, model):
        """
        Set model and modeladmin on which tool is acting
        for easy access in other methods.
        """
        from django.contrib.admin import site
        self.model = model
        self.modeladmin = site._registry.get(model)

    def construct_form(self, request):
        """
        Constructs form from POST method using self.form_class.
        """
        if not hasattr(self, 'form_class'):
            return None

        if request.method == 'POST':
            form = self.form_class(self.model, request.POST)
        else:
            form = self.form_class(self.model)
        return form

    def get_permission(self):
        return u'%s_%s' % (self.name, self.model._meta.object_name.lower())

    def has_permission(self, user):
        """
        Returns True if the given request has permission to use the tool.
        Can be overriden by the user in subclasses.
        """
        return user.has_perm(self.model._meta.app_label + '.' + \
                self.get_permission())

    def media(self, form):
        """
        Collects admin and form media.
        """
        js = ['js/core.js', 'js/admin/RelatedObjectLookups.js',
              'js/jquery.min.js', 'js/jquery.init.js']

        media = forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) \
                for url in js])

        if form:
            for name, field in form.fields.iteritems():
                media = media + field.widget.media

        return media

    def reverse(self):
        info = self.model._meta.app_label, self.model._meta.module_name, \
                self.name
        return reverse('object-tools:%s_%s_%s' % info)

    def _urls(self):
        """
        URL patterns for tool linked to _view method.
        """
        info = self.model._meta.app_label, self.model._meta.module_name, \
                self.name
        urlpatterns = patterns('',
            url(r'^%s/$' % self.name,
                self._view,
                name='%s_%s_%s' % info),
        )
        return urlpatterns
    urls = property(_urls)

    def construct_context(self, request):
        """
        Builds context with various required variables.
        """
        opts = self.model._meta
        app_label = opts.app_label
        object_name = opts.object_name.lower()
        form = self.construct_form(request)

        media = self.media(form)
        context = {
            'user': request.user,
            'title': '%s %s' % (self.label, opts.verbose_name_plural.lower()),
            'tool': self,
            'opts': opts,
            'app_label': app_label,
            'media': media,
            'form': form,
            'changelist_url': reverse('admin:%s_%s_changelist' % \
                    (app_label, object_name))
        }

        # Pass along fieldset if sepcififed.
        if hasattr(form, 'fieldsets'):
            admin_form = helpers.AdminForm(form, form.fieldsets, {})
            context['adminform'] = admin_form

        return context

    @csrf_protect_m
    def _view(self, request, extra_context=None):
        """
        View wrapper taking care of houskeeping for painless form rendering.
        """
        if not self.has_permission(request.user):
            raise PermissionDenied

        return self.view(request, self.construct_context(request))
