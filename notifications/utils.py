from django.contrib.auth.models import User, Group
from notifications.models import UserNotification

def check_full_name(user):
    u = User.objects.get(username=user)

    if not u.last_name and not u.first_name:
        user = u.username
    else:
        user = user.get_full_name()
    return user

def send_community_approval_notification(to_user, community):
    site_admins = User.objects.filter(groups__name='Site Administrator')

    title = "Your community application for "  +  str(community.community_name) + " was approved!"
    message = "You can customize Labels, creat projects and apply Labels to Notices."

    for admin in site_admins:
        UserNotification.objects.create(to_user=to_user, from_user=admin, title=title, message=message, notification_type="approval", community=community)


