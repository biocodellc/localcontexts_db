from django.db import models
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution

# Note: Right now all these fields are not required.
class Project(models.Model):
    title = models.TextField(blank=True, null=True)
    # contributor = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    target_species = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    publication_date = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    is_public = models.BooleanField(default=True, null=True)
    bclabels = models.ManyToManyField("bclabels.BCLabel", verbose_name="BC Labels", blank=True, related_name="project_labels")

    def has_labels(self):
        bc_labels = self.bclabels.count()
        if bc_labels > 0:
            return True
        else:
            return False

    def __str__(self):
        return self.title

class Researcher(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    # Note: for now orcid is not required, add unique = true later
    orcid = models.CharField(max_length=16, blank=True, null=True)
    projects = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return str(self.user)

class ProjectContributors(models.Model):
    project = models.OneToOneField(Project, null=True, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, null=True, blank=True, on_delete=models.DO_NOTHING)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'Project Contributors'
        verbose_name_plural = 'Project Contributors'
