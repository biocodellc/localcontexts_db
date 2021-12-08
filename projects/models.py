import uuid
from django.db import models
from django.contrib.auth.models import User
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher

class Project(models.Model):
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Sample', 'Sample'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    PRIVACY_LEVEL = {
        ('Public', 'Public'),
        ('Discoverable', 'Discoverable'),
        ('Private', 'Private')
    }
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, db_index=True)
    project_creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_creator")
    project_type = models.CharField(max_length=20, null=True, choices=TYPES)
    other_type = models.CharField(max_length=60, null=True, blank=True)
    project_privacy = models.CharField(max_length=20, null=True, choices=PRIVACY_LEVEL)
    title = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)
    project_contact = models.CharField(max_length=100, null=True)
    project_contact_email = models.EmailField(max_length=100, null=True)
    project_image = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    project_image2 = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    project_image3 = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    project_image4 = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    project_image5 = models.ImageField(upload_to='users/project-images', blank=True, null=True)
    publication_doi = models.CharField(max_length=200, blank=True, null=True)
    project_data_guid = models.CharField(max_length=200, blank=True, null=True)
    recommended_citation = models.TextField(null=True, blank=True)
    geome_project_id = models.IntegerField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    publication_date = models.DateField(null=True, blank=True)
    publication_date_ongoing = models.BooleanField(default=False, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    bc_labels = models.ManyToManyField("bclabels.BCLabel", verbose_name="BC Labels", blank=True, related_name="project_bclabels", db_index=True)
    tk_labels = models.ManyToManyField("tklabels.TKLabel", verbose_name="TK Labels", blank=True, related_name="project_tklabels", db_index=True)

    def has_labels(self):
        bc_labels = self.bc_labels.count()
        tk_labels = self.tk_labels.count()
        if bc_labels + tk_labels > 0:
            return True
        else:
            return False

    def has_notice(self):
        # Notices
        if self.project_notice.all().exists() or self.project_institutional_notice.all().exists():
            for notice in self.project_notice.all():
                if notice.archived:
                    return False
                else:
                    return True

            for inst_notice in self.project_institutional_notice.all():
                if inst_notice.archived:
                    return False
                else:
                    return True
        else:
            return False

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ('-date_added',)

class ProjectContributors(models.Model):
    project = models.OneToOneField(Project, related_name="project_contributors", null=True, on_delete=models.CASCADE)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="contributing_institutions")
    communities = models.ManyToManyField(Community, blank=True, related_name="contributing_communities")
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="contributing_researchers")

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'Project Contributors'
        verbose_name_plural = 'Project Contributors'

class ProjectPerson(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="additional_contributors")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        verbose_name = 'Additional Contributor'
        verbose_name_plural = 'Additional Contributors'