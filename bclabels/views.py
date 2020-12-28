from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *

@login_required(login_url='login')
def create_bclabel(request):
    l = BCLabel.objects.get(id=5)
    text = l.default_text

    context = {
        'text': text,
    }
    return render(request, 'bclabels/create.html', context)
