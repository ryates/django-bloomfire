from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from bloomfire import API

@login_required
def login(request, error_template=None):
    api = None
    try:
        api = API(
            settings.BLOOMFIRE_SUBDOMAIN,
            settings.BLOOMFIRE_API_KEY,
            settings.BLOOMFIRE_API_EMAIL,
            settings.BLOOMFIRE_API_PASSWORD
        )
        api_kwargs = {
            'membership[email]': request.user.email, 
            'membership[first_name]': request.user.first_name,
            'membership[last_name]': request.user.last_name,
            'auto_create_membership': 'true',
            'apikey': settings.BLOOMFIRE_API_KEY
        }
        try:
            default_password = settings.BLOOMFIRE_DEFAULT_PASSWORD
            api_kwargs['membership[password]'] = default_password
        except AttributeError:
            pass
        auth_result = api.post('memberships/new_token', api_kwargs)
        if settings.DEBUG:
            import sys
            sys.stderr.write('Bloomfire API: %s\n' % str(auth_result))
        
        if 'success' in auth_result and auth_result['success'] == 'true':
            return HttpResponseRedirect('https://%s.bloomfire.com/?token=%s' % (settings.BLOOMFIRE_SUBDOMAIN, auth_result['token'],))
        else:
            if 'errors' in auth_result:
                error_message = auth_result['errors']
            elif 'message' in auth_result:
                error_message = auth_result['message']
            else:
                error_message = 'Unexpected Error'
            return render_to_response(
                    error_template, 
                    {'error_message': error_message, 'api_result': auth_result}, 
                    context_instance=RequestContext(request)
                )
    except AttributeError:
        return HttpResponse('Site configuration problem - all of the following settings are required: BLOOMFIRE_SUBDOMAIN, BLOOMFIRE_API_KEY, BLOOMFIRE_API_EMAIL, BLOOMFIRE_API_PASSWORD')
