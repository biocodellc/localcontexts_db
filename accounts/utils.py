from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def get_users_name(user):
    if user is not None:
        if user.get_full_name():
            return user.get_full_name()
        else:
            return user.username
    else:
        return None

def manage_mailing_list(request, first_name, emailb64):
    selections = request.POST.getlist('topic')
    tech = 'no'
    news = 'no'
    events = 'no'
    notice = 'no'
    labels = 'no'
    for item in selections:
        if item == 'tech':
            tech = 'yes'
        if item == 'news':
            news = 'yes'
        if item == 'events':
            events = 'yes'
        if item == 'notice':
            notice = 'yes'
        if item == 'labels':
            labels = 'yes'
    variables = '{"first_name":"%s", "tech": "%s", "news": "%s", "events": "%s","notice": "%s","labels": "%s", "id": "%s"}'%(first_name, tech, news, events, notice, labels, emailb64)
    return(variables)