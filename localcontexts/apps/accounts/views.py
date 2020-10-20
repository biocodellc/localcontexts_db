from django.shortcuts import render, redirect
from django.contrib import messages, auth
from apps.accounts.models import Account
from django.core.mail import send_mail

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
            #Check that username exists
            if Account.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                #Check that email exists
                if Account.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    # If data unique, create user
                    user = Account.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

                    user.is_active = False
                    user.save()
                    return redirect('validate')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, "accounts/register.html")

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        # If user is found, log in the user.
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, "accounts/login.html")

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('index')

def dashboard(request):
    return render(request, "accounts/dashboard.html")

def validate(request):
    #TODO: figure out why this is not working
    # send_mail(
    #     'Subject',
    #     'Body text hello',
    #     'primallather@gmail.com',
    #     ['vofir28806@deselling.com'],
    #     fail_silently=False
    # )
    return render(request, 'accounts/validate.html')

def create_profile(request):
    return render(request, 'accounts/createprofile.html')

def connect_institution(request):
    return render(request, 'accounts/connect-institution.html')

def connect_community(request):
    return render(request, 'accounts/connect-community.html')