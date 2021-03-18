from django.db import models
from django.contrib.auth.models import User
from researchers.models import Researcher
from django_countries.fields import CountryField


class Institution(models.Model):
    institution_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='photos/institutions', blank=True, null=True)
    institution_name = models.CharField(max_length=80, blank=True, null=True)
    institution_id = models.CharField(max_length=80, blank=True, null=True)
    orcid = models.CharField(max_length=19, null=True, blank=True)
    contact_name = models.CharField(max_length=80, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    town_or_city = models.CharField(max_length=80, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="institution_members")

    def __str__(self):
        return self.institution_name

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
