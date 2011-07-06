from django.core.urlresolvers import reverse

class ObjectTool():
    def __init__(self, model):
        self.model = model

    def _view(self, request, extra_context=None):
        try:
            self.view
        except AttributeError:
            raise NotImplementedError('view method not implemented for %s' % self)

        opts = self.model._meta
        app_label = opts.app_label
        object_name = opts.object_name.lower()
        extra_context = {
            'user': request.user,
            'title': 'Export %s' % opts.verbose_name_plural.lower(),
            'tool': self,
            'opts': opts,
            'app_label': app_label,
            'changelist_url': reverse('admin:%s_%s_changelist' % (app_label, object_name))
        }
        return self.view(request, extra_context)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name, self.name

        urlpatterns = patterns('',
            url(r'^%s/$' % self.name,
                self._view,
                name='%s_%s_%s' % info),
        )
        return urlpatterns

    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    def reverse(self):
        info = self.model._meta.app_label, self.model._meta.module_name, self.name
        return reverse('object-tools:%s_%s_%s' % info)
