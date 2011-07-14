from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.admin import helpers
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
        Set model on which tool is acting for easy access in other methods.
        """
        self.model = model
    
    def construct_form(self, request):
        """
        Constructs form from POST method using self.form_class.
        """ 
        if request.method == 'POST':
            form = self.form_class(self.model, request.POST)
        else:
            form = self.form_class(self.model)
        return form
    
    def media(self, form):
        """
        Collects admin and form media.
        """
        js = ['js/core.js', 'js/admin/RelatedObjectLookups.js',
              'js/jquery.min.js', 'js/jquery.init.js']

        media = forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])
        
        for name, field in form.fields.iteritems():
            media = media + field.widget.media

        return media
    
    def reverse(self):
        info = self.model._meta.app_label, self.model._meta.module_name, self.name
        return reverse('object-tools:%s_%s_%s' % info)
    
    def _urls(self):
        """
        URL patterns for tool linked to _view method.
        """
        info = self.model._meta.app_label, self.model._meta.module_name, self.name
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
            'title': 'Export %s' % opts.verbose_name_plural.lower(),
            'tool': self,
            'opts': opts,
            'app_label': app_label,
            'media': media,
            'form': self.construct_form(request),
            'changelist_url': reverse('admin:%s_%s_changelist' % (app_label, object_name))
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
        return self.view(request, self.construct_context(request))
