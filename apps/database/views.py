from django.shortcuts import render

# Create your views here.
def home_screen_view(request):
    return render(request, "database/home.html", {})