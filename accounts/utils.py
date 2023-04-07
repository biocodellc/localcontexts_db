def get_users_name(user):
    if user is not None:
        if user.get_full_name():
            return user.get_full_name()
        else:
            return user.username
    else:
        return None

def manage_mailing_list(request, first_name):
    selections = request.POST.getlist('topic')
    tech = 'no'
    news = 'no'
    events = 'no'
    notices = 'no'
    labels = 'no'
    for item in selections:
        if item == 'tech':
            tech = 'yes'
        if item == 'news':
            news = 'yes'
        if item == 'events':
            events = 'yes'
        if item == 'notices':
            notices = 'yes'
        if item == 'labels':
            labels = 'yes'
    variables= '{"first_name":"%s", "tech": "%s", "news": "%s", "events": "%s","notices": "%s","labels": "%s"}'%(first_name, tech, news, events, notices, labels)
    return(variables)