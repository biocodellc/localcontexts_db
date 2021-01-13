from django.http import HttpResponse
from django.shortcuts import redirect


def allowed_users(allowed_roles=[]):
    def decorator(view_funct):
        def wrapper_funct(request, *args, **kawrgs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_funct(request, *args, **kawrgs)
            else:
                return HttpResponse('Not authorized')
        return wrapper_funct
    return decorator

def admin_only(view_funct):
    def wrapper_funct(request, *args, **kwargs):
        group = None 
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        
        if group == 'editor':
            return redirect('dashboard')
        
        if group == 'viewer':
            return view_funct(request, *args, **kawrgs)
    
    return wrapper_funct

    