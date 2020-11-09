from django.http import HttpResponse
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


class HealthCheck(View):
    def get(self, request):
        return HttpResponse("ok", content_type="text/plain")


index = never_cache(TemplateView.as_view(template_name='index.html'))
