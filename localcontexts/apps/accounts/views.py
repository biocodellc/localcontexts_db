from django.shortcuts import render, redirect
from django.contrib import messages, auth
from apps.accounts.models import Account

# Create your views here.

def register(request):
    if request.method == 'POST':
        #Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        #Check for password match
        if password == password2:
            #Check username
            if Account.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                if Account.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    #TODO: Fix this! create_user not working because of custom user model?
                    # Also do we need a user_auth table with custom user?
                    # AND: look into forms.py

                    # If this works, create user
                    user = Account.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                    
                    # Use the following if you want to Login after register
                    # auth.login(request, user)
                    # messages.success(request, 'User is now logged in')
                    # return redirect('index')
                    user.save()
                    messages.success(request, 'You are registered')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, "accounts/register.html")

def login(request):
    if request.method == 'POST':
        print('logged in')
        return redirect('index')
    else:
        return render(request, "accounts/login.html")

def logout(request):
    return redirect('index')

def dashboard(request):
    return render(request, "accounts/dashboard.html")