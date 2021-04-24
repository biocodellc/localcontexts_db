import uuid
from django.db import models
from communities.models import Community
from researchers.models import Researcher
from institutions.models import Institution
from projects.models import Project
from django.contrib.auth.models import User
from bclabels.models import NoticeStatus

class TKNotice(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    communities = models.ManyToManyField(Community, blank=True, related_name="tknotice_communities")
    statuses = models.ManyToManyField(NoticeStatus, blank=True, related_name="tknotice_statuses")
    placed_by_researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True)
    placed_by_institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True)
    message = models.TextField(max_length=1500, null=True, blank=True) #250 word limit on message
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.project)
    
    class Meta:
        verbose_name = 'TK Notice'
        verbose_name_plural = 'TK Notices'
        ordering = ('-created',)

class TKLabel(models.Model):
    TYPES = (
        ('attribution', 'attribution'),
        ('clan', 'clan'),
        ('family', 'family'),
        ('outreach', 'outreach'),
        ('tk_multiple_community', 'tk_multiple_community'),
        ('non_verified', 'non_verified'),  
        ('verified', 'verified'),  
        ('non_commercial', 'non_commercial'),  
        ('commercial', 'commercial'),  
        ('culturally_sensitive', 'culturally_sensitive'),  
        ('community_voice', 'community_voice'),  
        ('community_use_only', 'community_use_only'),  
        ('seasonal', 'seasonal'),  
        ('women_general', 'women_general'),  
        ('men_general', 'men_general'),  
        ('men_restricted', 'men_restricted'),  
        ('women_restricted', 'women_restricted'),  
        ('secret_sacred', 'secret_sacred'),  
    )
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="tklabel_creator")
    label_type = models.CharField(max_length=50, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='label name', max_length=90, null=True)
    default_text = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="tklabel_approver")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.community) + ' ' + str(self.label_type) + ' ' + str(self.name)
    
    class Meta:
        verbose_name = 'TK Label'
        verbose_name_plural = 'TK Labels'
        ordering = ('-created',)
