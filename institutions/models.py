from django.db import models
from django.contrib.auth.models import User
from researchers.models import Researcher
from django_countries.fields import CountryField


class Institution(models.Model):
    institution_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    institution_name = models.CharField(max_length=80, null=True, unique=True)
    contact_name = models.CharField(max_length=80, null=True)
    contact_email = models.EmailField(max_length=254, null=True)
    image = models.ImageField(upload_to='users/institution-images', blank=True, null=True)
    description = models.TextField(null=True)
    institution_id = models.CharField(max_length=80, blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    town_or_city = models.CharField(max_length=80, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, related_name="institution_admins")
    editors = models.ManyToManyField(User, blank=True, related_name="institution_editors")
    viewers = models.ManyToManyField(User, blank=True, related_name="institution_viewers")
    projects = models.ManyToManyField('projects.Project', blank=True, related_name="institution_projects")
    is_approved = models.BooleanField(default=False, null=True)
    is_ror = models.BooleanField(default=True, null=False)

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
        return str(self.institution_name)

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
