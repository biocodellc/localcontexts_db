from django.db import models
from django.contrib.auth.models import User

# Note: Right now all these fields are not required.
class Project(models.Model):
    title = models.TextField(blank=True, null=True)
    contributor = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    target_species = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    publication_date = models.TextField(blank=True, null=True)
    date_added = models.TextField(blank=True, null=True)
    date_modified = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.who

class Researcher(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    # Note: for now orcid is not required
    orcid = models.CharField(max_length=16, blank=True, null=True)
    projects = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return str(self.user)
