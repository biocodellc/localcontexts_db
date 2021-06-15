from django.db import models
from django.contrib.auth.models import User

class Researcher(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    orcid = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to='users/researcher-images', blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    associated_institution = models.CharField(max_length=250, null=True, blank=True)
    location = models.CharField(max_length=300, null=True, blank=True)
    projects = models.ManyToManyField('projects.Project', blank=True, related_name="researcher_projects")

    def __str__(self):
        return str(self.user)
