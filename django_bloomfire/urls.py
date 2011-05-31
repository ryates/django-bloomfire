from django.conf.urls.defaults import *

urlpatterns = patterns('django_bloomfire.views',
    url(r'^login/$', 'login', {'error_template': 'bloomfire/error.html'}, name='bloomfire-login'),
)