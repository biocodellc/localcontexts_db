from django.shortcuts import render

# Create your views here.
def home_screen_view(request):
    return render(request, "accounts/home.html", {})

def register_screen_view(request):
    return render(request, "accounts/register.html")