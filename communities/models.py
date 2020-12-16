from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.conf import settings

class Community(models.Model):
    community_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='photos/communities', blank=True, null=True)
    community_name = models.CharField(max_length=80, blank=True, null=True)
    community_code = models.CharField(max_length=80, blank=True, null=True)
    town = models.CharField(max_length=80, blank=True, null=True)
    contact_name = models.CharField(max_length=80, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    is_publicly_listed = models.BooleanField(default=True, null=True)
    editors = models.ManyToManyField(User, blank=True, related_name="editors")
    viewers = models.ManyToManyField(User, blank=True, related_name="viewers")

    def get_member_count(self):
        editors = self.editors.count()
        viewers = self.viewers.count()
        total_members = editors + viewers + 1
        return total_members
    
    def get_editors(self):
        return self.editors.all()
    
    def get_viewers(self):
        return self.viewers.all()

    def __str__(self):
        return str(self.community_name)

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'

class UserCommunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="user_communities")

    @classmethod
    def create(cls, user):
        obj = cls(user=user)
        return obj

    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = 'User Communities'

class InviteMember(models.Model):
    STATUS_CHOICES = (
        ('sent', 'sent'),
        ('accepted', 'accepted'),
    )

    ROLES = (
        ('editor', 'editor'),
        ('viewer', 'viewer'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community', null=True)
    role = models.CharField(max_length=8, choices=ROLES, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"