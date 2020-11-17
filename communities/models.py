from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Community(models.Model):
    image = models.ImageField(upload_to='photos/communities', blank=True, null=True)
    community_name = models.CharField(max_length=80, blank=True, null=True)
    community_code = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=80, blank=True, null=True)
    contact_name = models.CharField(max_length=80, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    is_publicly_listed = models.BooleanField(default=True, null=True)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.community_name

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'

class UserCommunity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    communities = models.ManyToManyField(Community, blank=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = 'User Communities'


