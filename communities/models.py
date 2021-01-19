from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.conf import settings

class Community(models.Model):
    community_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='photos/communities', blank=True, null=True)
    community_name = models.CharField(max_length=80, null=True)
    community_code = models.CharField(max_length=80, blank=True, null=True)
    contact_name = models.CharField(max_length=80, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    town = models.CharField(max_length=80, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, related_name="admins")
    editors = models.ManyToManyField(User, blank=True, related_name="editors")
    viewers = models.ManyToManyField(User, blank=True, related_name="viewers")
    is_publicly_listed = models.BooleanField(default=True, null=True)
    is_approved = models.BooleanField(default=False, null=True)


    def get_member_count(self):
        admins = self.admins.count()
        editors = self.editors.count()
        viewers = self.viewers.count()
        total_members = admins + editors + viewers + 1
        return total_members
        
    def get_admins(self):
        return self.admins.all()

    def get_editors(self):
        return self.editors.all()
    
    def get_viewers(self):
        return self.viewers.all()

    def __str__(self):
        return str(self.community_name)

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'

class InviteMember(models.Model):
    STATUS_CHOICES = (
        ('sent', 'sent'),
        ('accepted', 'accepted'),
    )

    ROLES = (
        ('admin', 'admin'),
        ('editor', 'editor'),
        ('viewer', 'viewer'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community', null=True)
    role = models.CharField(max_length=8, choices=ROLES, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='sent')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
    
    class Meta:
        verbose_name = 'Member Invitation'
        verbose_name_plural = 'Member Invitations'

class CommunityJoinRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'sent'),
        ('accepted', 'accepted'),
    )
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_from')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_to')
    target_community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='target_community', null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='sent')
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_from}-{self.user_to}-{self.target_community}-{self.status}"

    class Meta:
        verbose_name = 'Community Join Request'
        verbose_name_plural = 'Community Join Requests'