from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Community(models.Model):
    image = models.ImageField(upload_to='photos/communities', blank=True, null=True)
    community_name = models.CharField(max_length=80)
    community_code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)
    country = CountryField()
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.community_name

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'

class UserCommunity(models.Model):
    name = models.CharField(max_length=10, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    communities = models.ManyToManyField(Community)
    # roles = models.ManyToManyField(Role)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = 'User Communities'


