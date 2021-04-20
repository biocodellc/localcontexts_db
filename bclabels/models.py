import uuid
from django.db import models
from communities.models import Community
from researchers.models import Researcher
from institutions.models import Institution
from projects.models import Project
from django.contrib.auth.models import User

class NoticeStatus(models.Model):
    CHOICES = (
        ('pending', 'pending'),
        ('not_pending', 'not_pending'),
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="status_community", blank=True)
    seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.community} - {self.seen} - {self.status}"

    class Meta:
        verbose_name = 'Notice Status'
        verbose_name_plural = 'Notice Status'
        

class BCNotice(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    communities = models.ManyToManyField(Community, blank=True, related_name="bcnotice_communities")
    statuses = models.ManyToManyField(NoticeStatus, blank=True, related_name="bcnotice_statuses")
    placed_by_researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True)
    placed_by_institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True)
    message = models.TextField(max_length=1500, null=True, blank=True) #250 word limit on message
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.project.title)
    
    class Meta:
        verbose_name = 'BC Notice'
        verbose_name_plural = 'BC Notices'
        ordering = ('-created',)


class BCLabel(models.Model):
    TYPES = (
        ('provenance', 'provenance'),
        ('commercialization', 'commercialization'),
        ('collaboration', 'collaboration'),
        ('consent_verified', 'consent_verified'),
        ('multiple_community', 'multiple_community'),
        ('research', 'research'),  
    )
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="bclabel_creator")
    label_type = models.CharField(max_length=20, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='label name', max_length=90, null=True)
    bc_notice = models.ForeignKey(BCNotice, null=True, on_delete=models.DO_NOTHING, blank=True)
    default_text = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="bclabel_approver")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.community) + ' ' + str(self.label_type) + ' ' + str(self.name)
    
    class Meta:
        verbose_name = 'BC Label'
        verbose_name_plural = 'BC Labels'
        ordering = ('-created',)
