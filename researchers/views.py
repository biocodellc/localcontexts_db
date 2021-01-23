from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Researcher
from .forms import ConnectResearcherForm

@login_required(login_url='login')
def connect_researcher(request):
    form = ConnectResearcherForm()

    if request.method == "POST":
        form = ConnectResearcherForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('researcher-dashboard')

    return render(request, 'researchers/connect-researcher.html', {'form': form})

@login_required(login_url='login')
def researcher_dashboard(request, pk):
    # is current user a researcher?
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/dashboard.html', {'researcher': researcher})