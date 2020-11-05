from django.db import models
from django.contrib.auth.models import User

# Note: Right now all these fields are not required.
class Project(models.Model):
    who = models.TextField(blank=True, null=True)
    when = models.TextField(blank=True, null=True)
    where = models.TextField(blank=True, null=True)
    what = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    target_species = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.who

class Researcher(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    # Note: for now orcid is not required
    orcid = models.CharField(max_length=16, blank=True, null=True)
    project = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return str(self.user)
