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
        ('Samples', 'Samples'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    PRIVACY_LEVEL = {
        ('Public', 'Public'),
        ('Discoverable', 'Discoverable'),
        ('Private', 'Private'),
    }
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, db_index=True)
    project_creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_creator")
    project_page = models.URLField(blank=True, null=True)
    project_type = models.CharField(max_length=20, null=True, choices=TYPES)
    other_type = models.CharField(max_length=60, null=True, blank=True)
    project_privacy = models.CharField(max_length=20, null=True, choices=PRIVACY_LEVEL)
    title = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)
    project_contact = models.CharField(max_length=100, null=True)
    project_contact_email = models.EmailField(max_length=100, null=True)
    publication_doi = models.CharField(max_length=200, blank=True, null=True)
    project_data_guid = models.CharField(max_length=200, blank=True, null=True)
    providers_id = models.CharField(max_length=200, blank=True, null=True)
    project_boundary_geojson = models.JSONField(blank=True, null=True)
    urls = models.JSONField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    bc_labels = models.ManyToManyField("bclabels.BCLabel", verbose_name="BC Labels", blank=True, related_name="project_bclabels", db_index=True)
    tk_labels = models.ManyToManyField("tklabels.TKLabel", verbose_name="TK Labels", blank=True, related_name="project_tklabels", db_index=True)

    def has_labels(self):
        if self.bc_labels.exists() or self.tk_labels.exists():
            return True
        else:
            return False
    
    def has_bclabels(self):
        if self.bc_labels.exists():
            return True
        else:
            return False
    
    def has_tklabels(self):
        if self.tk_labels.exists():
            return True
        else:
            return False

    def has_notice(self):
        if self.project_notice.exists():
            if self.project_notice.filter(archived=True).exists():
                return False
            elif self.project_notice.filter(archived=False).exists():
                return True
        else:
            return False

    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [models.Index(fields=['unique_id', 'project_creator'])]
        ordering = ('-date_added',)

class ProjectContributors(models.Model):
    project = models.OneToOneField(Project, related_name="project_contributors", null=True, on_delete=models.CASCADE)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="contributing_institutions")
    communities = models.ManyToManyField(Community, blank=True, related_name="contributing_communities")
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="contributing_researchers")

    def __str__(self):
        return str(self.project)

    class Meta:
        indexes = [models.Index(fields=['project'])]
        verbose_name = 'Project Contributors'
        verbose_name_plural = 'Project Contributors'

class ProjectPerson(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="additional_contributors")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project'])]
        verbose_name = 'Additional Contributor'
        verbose_name_plural = 'Additional Contributors'

class ProjectCreator(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_created_project', null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='institution_created_project', null=True, blank=True)
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE, related_name='researcher_created_project', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_creator_project', null=True, blank=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'community', 'institution', 'researcher'])]
        verbose_name = 'Project Creator'
        verbose_name_plural = 'Project Creator'

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_note', null=True, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_note', null=True, blank=True)
    note = models.TextField('Community Note', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'community'])]
        verbose_name = 'Project Note'
        verbose_name_plural = 'Project Notes'
