from .models import Researcher

def is_user_researcher(user):
    if Researcher.objects.filter(user=user).exists():
        return Researcher.objects.select_related('user').get(user=user)
    else:
        return False

def checkif_user_researcher(current_researcher, user):
    if Researcher.objects.filter(user=user).exists():
        researcher = Researcher.objects.select_related('user').get(user=user)
        if current_researcher == researcher:
            return True
        else:
            return False
    else:
        return False