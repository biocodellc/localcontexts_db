import uuid
from django.db import models
from communities.models import Community
from researchers.models import Researcher
from institutions.models import Institution
from projects.models import Project
from django.contrib.auth.models import User

class BCLabel(models.Model):
    TYPES = (
        ('provenance', 'provenance'),
        ('commercialization', 'commercialization'),
        ('non_commercial', 'non_commercial'),  
        ('collaboration', 'collaboration'),
        ('consent_verified', 'consent_verified'),
        ('consent_non_verified', 'consent_non_verified'),
        ('multiple_community', 'multiple_community'),
        ('research', 'research'),  
        ('clan', 'clan'),
        ('outreach', 'outreach'),  
    )
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="bclabel_creator")
    label_type = models.CharField(max_length=20, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='label name', max_length=90, null=True)
    default_text = models.TextField(null=True, blank=True)
    img_url = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="bclabel_approver")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.community) + ' ' + str(self.label_type) + ' ' + str(self.name)
    
    class Meta:
        verbose_name = 'BC Label'
        verbose_name_plural = 'BC Labels'
        ordering = ('-created',)
