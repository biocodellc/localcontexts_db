from django.db import models
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution

# Note: Right now all these fields are not required.
class Project(models.Model):
    title = models.TextField(null=True, required=True)
    description = models.TextField(null=True, required=True)
    principal_investigator = models.CharField(max_length=100, blank=True, null=True)
    principal_investigator_affiliation = models.CharField(max_length=100, blank=True, null=True)
    project_contact = models.CharField(max_length=100, blank=True, null=True)
    project_contact_email = models.EmailField(max_length=100, blank=True, null=True)
    publication_doi = models.CharField(max_length=200, blank=True, null=True)
    project_data_guid = models.CharField(max_length=200, blank=True, null=True)
    geome_project_id = models.IntegerField(max_length=10, blank=True, null=True)
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
    
    class Meta:
        ordering = ('-date_added',)

class Researcher(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    # Note: for now orcid is not required, add unique = true later
    orcid = models.CharField(max_length=16, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(max_length=150, blank=True, null=True)
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
