from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.conf import settings
from institutions.models import Institution
import uuid
import os

def get_file_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('communities/support-files', filename)  

class Community(models.Model):
    community_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    community_name = models.CharField(max_length=80, null=True, unique=True)
    community_entity = models.CharField(max_length=200, null=True, blank=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_email = models.EmailField(max_length=254, null=True, blank=True)
    image = models.ImageField(upload_to='users/community-images', blank=True, null=True)
    support_document = models.FileField(upload_to=get_file_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True, validators=[MaxLengthValidator(200)])
    city_town = models.CharField(max_length=80, blank=True, null=True)
    state_province_region = models.CharField(verbose_name='state or province', max_length=100, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, related_name="admins", db_index=True)
    editors = models.ManyToManyField(User, blank=True, related_name="editors", db_index=True)
    viewers = models.ManyToManyField(User, blank=True, related_name="viewers", db_index=True)
    is_publicly_listed = models.BooleanField(default=False, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    projects = models.ManyToManyField('projects.Project', blank=True, related_name="community_projects", db_index=True)

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
    
    def is_user_in_community(self, user):
        if user in self.viewers.all() or user in self.editors.all() or user in self.admins.all() or user == self.community_creator:
            return True
        else:
            return False

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

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_invitation', null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='institution_invitation', null=True, blank=True)
    role = models.CharField(max_length=8, choices=ROLES, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='sent', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
    
    class Meta:
        verbose_name = 'Member Invitation'
        verbose_name_plural = 'Member Invitations'
        ordering = ('-created',)

class JoinRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'sent'),
        ('accepted', 'accepted'),
    )

    ROLES = (
        ('admin', 'admin'),
        ('editor', 'editor'),
        ('viewer', 'viewer'),
    )

    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_sender')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_receiver')
    role = models.CharField(max_length=8, choices=ROLES, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='join_request_community', null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='join_request_institution', null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='sent')
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_from}-{self.user_to}-{self.status}"

    class Meta:
        verbose_name = 'Join Request'
        verbose_name_plural = 'Join Requests'
        ordering = ('-date_sent',)