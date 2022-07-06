import uuid
from django.db import models
from communities.models import Community
from django.contrib.auth.models import User
import os

def tklabel_audio_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(self.unique_id), ext)
    return os.path.join('communities/tklabel-audiofiles', filename)

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
        ('open_to_collaboration', 'open_to_collaboration'),  
        ('creative', 'creative'),  
    )
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="tklabel_creator")
    label_type = models.CharField(max_length=50, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='label name', max_length=90, null=True)
    language_tag = models.CharField(max_length=5, blank=True)
    language = models.CharField(max_length=150, blank=True)
    label_text = models.TextField(null=True, blank=True)
    img_url = models.URLField(blank=True, null=True)
    svg_url = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tklabel_approver")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    audiofile = models.FileField(upload_to=tklabel_audio_path, blank=True)

    def __str__(self):
        return str(self.community) + ' ' + str(self.label_type) + ' ' + str(self.name)
    
    class Meta:
        verbose_name = 'TK Label'
        verbose_name_plural = 'TK Labels'
        ordering = ('-created',)

