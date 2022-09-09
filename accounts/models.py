from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

from communities.models import Community
from institutions.models import Institution

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='photos/', blank=True, null=True, default='default.png')
    city_town = models.CharField(verbose_name='city or town', max_length=80, blank=True, null=True)
    state_province_region = models.CharField(verbose_name='state or province', max_length=100, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    position = models.CharField(verbose_name='position', max_length=80, blank=True, null=True)
    affiliation = models.CharField(verbose_name='affiliation', max_length=250, blank=True, null=True)
    preferred_language = models.CharField(verbose_name='preferred language', max_length=80, blank=True, null=True)
    languages_spoken = models.CharField(verbose_name='languages spoken', max_length=150, blank=True, null=True)    
    is_researcher = models.BooleanField(default=False, null=True)
    onboarding_on = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        indexes = [models.Index(fields=['user'])]

class UserAffiliation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="user_communities")
    institutions = models.ManyToManyField(Institution, blank=True, related_name="user_institutions")

    @classmethod
    def create(cls, user):
        obj = cls(user=user)
        return obj

    def __str__(self):
        return str(self.user)
    
    class Meta:
        indexes = [models.Index(fields=['user'])]
        verbose_name = 'User Affiliation'
        verbose_name_plural = 'User Affiliations'

class SignUpInvitation(models.Model):
    email = models.EmailField(null=True)
    message = models.TextField(max_length=120, null=True, blank=True)
    sender = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "Sign Up Invitation"        
        verbose_name_plural = "Sign Up Invitations"
        ordering = ('-date_sent',)