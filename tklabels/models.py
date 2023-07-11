import json
import uuid
from django.db import models
from communities.models import Community
from django.contrib.auth.models import User
import os
import requests

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
    version = models.SmallIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="tklabel_creator")
    label_type = models.CharField(max_length=50, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE, related_name='tklabel_community')
    name = models.CharField(verbose_name='label name', max_length=90, null=True, blank=True)
    language_tag = models.CharField(max_length=5, blank=True)
    language = models.CharField(max_length=150, blank=True, default="English")
    label_text = models.TextField(null=True, blank=True)
    img_url = models.URLField(blank=True, null=True)
    svg_url = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tklabel_approver")
    last_edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tklabel_last_edited_by")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    audiofile = models.FileField(upload_to=tklabel_audio_path, blank=True)

    def save(self, *args, **kwargs):
        # set up language tag
        url = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
        data = requests.get(url).json()

        if self.language in data.keys():
            self.language_tag = data[self.language]

        # set up label defaults (img + svg)
        json_data = open('./localcontexts/static/json/Labels.json')
        data = json.load(json_data) #deserialize

        baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/tklabels/'
        for key, values in data.items():
            if key == 'tkLabels':
                if(isinstance(values, list)):
                    for value in values:
                        if self.label_type == value['labelType']:
                            self.img_url = baseURL + value['imgFileName']
                            self.svg_url = baseURL + value['svgFileName']
                        elif self.label_type == 'placeholder':
                            self.img_url = None
                            self.svg_url = None
                            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.community} - {self.name}"
    
    class Meta:
        indexes = [models.Index(fields=['unique_id', 'created_by', 'community', 'is_approved', 'approved_by', 'audiofile'])]
        verbose_name = 'TK Label'
        verbose_name_plural = 'TK Labels'
        ordering = ('-created',)

