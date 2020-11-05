from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class Institution(models.Model):
    image = models.ImageField(upload_to='photos/institutions', blank=True, null=True)
    institution_name = models.CharField(max_length=80)
    institution_code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)
    country = CountryField()
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.institution_name

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'

class UserInstitution(models.Model):
    name = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    institution = models.ManyToManyField(Institution)
    # roles = models.ManyToManyField(Role)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Institution'
        verbose_name_plural = 'User Institutions'
