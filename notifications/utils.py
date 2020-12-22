from django.contrib.auth.models import User

def check_full_name(user):
    u = User.objects.get(username=user)

    if not u.last_name and not u.first_name:
        user = u.username
    else:
        user = user.get_full_name()
    return user