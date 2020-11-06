from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class Institution(models.Model):
    image = models.ImageField(upload_to='photos/institutions', blank=True, null=True)
    institution_name = models.CharField(max_length=80, blank=True, null=True)
    institution_code = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=80, blank=True, null=True)
    contact_name = models.CharField(max_length=80, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.institution_name

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'

class UserInstitution(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    institution = models.ManyToManyField(Institution, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Institution'
        verbose_name_plural = 'User Institutions'
