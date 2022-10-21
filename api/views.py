from django.shortcuts import redirect
current_version = '/api/v1/'

def redirect_view(request):
    response = redirect(current_version)
    return response
