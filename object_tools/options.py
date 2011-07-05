from django.core.urlresolvers import reverse

class ObjectTool():
    def __init__(self, model):
        self.model = model

    def view(self, request, extra_context=None):
        raise NotImplementedError('view method not implemented for %s' % self)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name, self.name

        urlpatterns = patterns('',
            url(r'^%s/$' % self.name,
                self.view,
                name='%s_%s_%s' % info),
        )
        return urlpatterns

    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    def reverse(self):
        info = self.model._meta.app_label, self.model._meta.module_name, self.name
        return reverse('object-tools:%s_%s_%s' % info)
