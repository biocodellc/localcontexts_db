from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from communities.models import UserCommunity

# When a user is saved, send this signal (Create User Profile instance)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# When a user is saved, create UserCommunity instance
@receiver(post_save, sender=User)
def create_usercommunity(sender, instance, created, **kwargs):
    if created:
        UserCommunity.objects.create(user=instance)

post_save.connect(create_usercommunity, sender=User)

#TODO: figure out how this will work in community context and if we need it at all
# @receiver(post_save, sender=CommunityInvitation)
# def add_community_member(sender, created, instance, **kwargs):
#     sender_ = instance.sender
#     receiver_ = instance.receiver
#     if instance.status=='accepted':
        # If invitation is accepted
        # Receiver's usercommunity is updated with sender's Community
        # Community is updated with member based on role
        # target_user=UserCommunity.objects.get(username=receiver_.user.username)
        # target_user.communities.add(sender_.community_name)

        # if instance.role=='editor':
        #     sender_.editor.add(receiver_.user)

        # elif instance.role=='viewer':
        #     sender_.viewer.add(receiver_.user)

        # sender_.save()
        # target_user.save()