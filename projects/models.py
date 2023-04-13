import uuid
from django.db import models
from django.contrib.auth.models import User
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher
from helpers.utils import discoverable_project_view

class ProjectArchived(models.Model):
    project_uuid = models.UUIDField(null=True, blank=True, db_index=True)
    community_id = models.IntegerField(null=True, blank=True)
    institution_id = models.IntegerField(null=True, blank=True)
    researcher_id = models.IntegerField(null=True, blank=True)
    archived = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Project Archived'

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
        ('Contributor', 'Contributor'),
        ('Private', 'Private'),
    }
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, db_index=True, verbose_name="Unique ID (UUID)")
    project_creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_creator")
    project_page = models.URLField(blank=True, null=True)
    project_type = models.CharField(max_length=20, null=True, choices=TYPES)
    other_type = models.CharField(max_length=60, null=True, blank=True)
    project_privacy = models.CharField(max_length=20, null=True, choices=PRIVACY_LEVEL)
    title = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)
    project_contact = models.CharField(max_length=100, null=True)
    project_contact_email = models.EmailField(max_length=100, null=True)
    publication_doi = models.CharField(max_length=200, blank=True, null=True, verbose_name="Publication DOI")
    project_data_guid = models.CharField(max_length=200, blank=True, null=True, verbose_name="Project data GUID")
    providers_id = models.CharField(max_length=200, blank=True, null=True, verbose_name="Provider's ID")
    project_boundary_geojson = models.JSONField(blank=True, null=True, verbose_name="Project boundary GeoJSON")
    urls = models.JSONField(blank=True, null=True, verbose_name="URLs")
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    source_project_uuid = models.UUIDField(null=True, verbose_name="Source Project UUID", blank=True, db_index=True)
    related_projects = models.ManyToManyField("self", blank=True, verbose_name="Related Projects", related_name="related_projects", db_index=True)
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
    
    @property
    def is_sub_project(self):
        if self.source_project_uuid is not None:
            return True
        else:
            return False

    def can_user_access(self, user):
        # returns either True, False, or 'partial'
        if user == self.project_creator:
            return True
        elif self.project_privacy == 'Public':
            return True
        elif self.project_privacy == 'Contributor':
            return discoverable_project_view(self, user)
        elif self.project_privacy == 'Private':
            return False
    
    def get_template_name(self, user):
        if self.project_privacy == 'Public':
            return 'partials/_project-actions.html'
        elif self.project_privacy == 'Contributor':
            if not discoverable_project_view(self, user) == 'partial':
                return 'partials/_project-actions.html'
            else:
                return 'partials/_project-contributor-view.html'
        elif self.project_privacy == 'Private' and user == self.project_creator:
            return 'partials/_project-actions.html'
        else:
            return None
    

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

    def is_user_contributor(self, user):
        is_contributor = False
        for community in self.communities.all():
            if community.is_user_in_community(user):
                is_contributor = True
                break
        for institution in self.institutions.all():
            if institution.is_user_in_institution(user):
                is_contributor = True
                break
        for researcher in self.researchers.all():
            if user == researcher.user:
                is_contributor = True
                break
        return is_contributor

    def __str__(self):
        return str(self.project)

    class Meta:
        indexes = [models.Index(fields=['project'])]
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

    def which_account_type_created(self):
        #  returns dictionary
        is_created_by = { 'community': False, 'institution': False, 'researcher': False,}
        if self.community:
            is_created_by['community'] = True
        if self.institution:
            is_created_by['institution'] = True
        if self.researcher:
            is_created_by['researcher'] = True
        return is_created_by
    
    def is_user_in_creator_account(self, user, is_created_by):
        is_user_in_account = False
        if is_created_by['community'] and self.community.is_user_in_community(user): # is user a member of the community that created the project
            is_user_in_account = True
        elif is_created_by['institution'] and self.institution.is_user_in_institution(user): # is user a member of the institution tha created the project
            is_user_in_account = True
        elif is_created_by['researcher'] and Researcher.objects.filter(user=user).exists() and self.researcher == Researcher.objects.get(user=user): # does this user have a researcher account and is it the same researcher account which created the project 
            is_user_in_account = True
        else:
            is_user_in_account = False
        return is_user_in_account


    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'community', 'institution', 'researcher'])]
        verbose_name_plural = 'Project Creator'

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_note', null=True, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_note', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="project_note_sender", blank=True)
    note = models.TextField('Community Note', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'community'])]
        verbose_name_plural = 'Project Notes'

class ProjectActivity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_activity', null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    activity = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        indexes = [models.Index(fields=['project'])]
        verbose_name_plural = 'Project Activity'
