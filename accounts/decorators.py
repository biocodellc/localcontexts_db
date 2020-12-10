from django.http import HttpResponse
from django.shortcuts import redirect
 
# a function that takes in another function as a parameter 
# and lets us add more functionality before the desired function is called.

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        # If user is authenticated, takes the user to dashboard, otherwise shows desired view.
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

# TODO: would this help with different views 
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)

            else: 
                return HttpResponse('Not authorized to view this page')
        return wrapper_func
    return decorator

#TODO: Figure out if this is helpful for how roles are determined.
def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        group= None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        
        if group == 'editor':
            return redirect('dashboard')
        
        if group == 'viewer':
            return redirect('dashboard')

        if group == 'admin':
            return view_func(request, *args, **kwargs)

    return wrapper_func
