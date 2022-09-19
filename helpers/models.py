import json
import requests
from django.db import models
from django.contrib.auth.models import User
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from communities.models import Community
from projects.models import Project
from researchers.models import Researcher
from institutions.models import Institution

class Notice(models.Model):
    TYPES = (
        ('biocultural', 'biocultural'),
        ('traditional_knowledge', 'traditional_knowledge'),
        ('attribution_incomplete', 'attribution_incomplete'),
    )
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="project_notice", db_index=True)
    notice_type = models.CharField(max_length=50, null=True, choices=TYPES)
    name = models.CharField(max_length=60, null=True, blank=True)
    researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    img_url = models.URLField(blank=True, null=True)
    svg_url = models.URLField(blank=True, null=True)
    default_text = models.TextField(null=True, blank=True)
    archived = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        json_data = open('./localcontexts/static/json/Notices.json')
        data = json.load(json_data) #deserialize

        baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/'
        for item in data:
            if item['noticeType'] == self.notice_type:
                self.name = item['noticeName']
                self.img_url = baseURL + item['imgFileName']
                self.svg_url = baseURL + item['svgFileName']
                self.default_text = item['noticeDefaultText']

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.project.title)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'researcher', 'institution'])]
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
        ordering = ('-created',)

class OpenToCollaborateNoticeURL(models.Model):
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    url = models.URLField(null=True)
    added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        indexes = [models.Index(fields=['institution', 'researcher'])]
        verbose_name = 'Open To Collaborate Notice URL'
        verbose_name_plural = 'Open To Collaborate Notice URLs'

class EntitiesNotified(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="project_notified", db_index=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="communities_notified", db_index=True)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="institutions_notified", db_index=True)
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="researchers_notified", db_index=True)

    def __str__(self):
        return str(self.project.title)
    
    class Meta:
        indexes = [models.Index(fields=['project'])]
        verbose_name = "Entities Notified"
        verbose_name_plural = "Entities Notified"

class LabelTranslation(models.Model):
    bclabel = models.ForeignKey(BCLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="bclabel_translation")
    tklabel = models.ForeignKey(TKLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="tklabel_translation")
    translated_name = models.CharField(max_length=150, blank=True)
    language_tag = models.CharField(max_length=5, blank=True)
    language = models.CharField(max_length=150, blank=True)
    translated_text = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # set up language tag
        url = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
        data = requests.get(url).json()

        if self.language in data.keys():
            self.language_tag = data[self.language]

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.translated_name)
    
    class Meta:
        indexes = [models.Index(fields=['bclabel', 'tklabel'])]
        verbose_name = "Label Translation"
        verbose_name_plural = "Label Translations"

class ProjectComment(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="project_comment", db_index=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="comment_community", blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="comment_sender", blank=True)
    message = models.TextField(max_length=1500, null=True, blank=True) #250 word limit on message
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return 'Comment {} by {}'.format(self.message, self.community)

    class Meta:
        indexes = [models.Index(fields=['project', 'community', 'sender'])]
        verbose_name = 'Project Comment'
        verbose_name_plural = 'Project Comments'
        ordering = ('created',)

class ProjectStatus(models.Model):
    CHOICES = (
        ('pending', 'pending'),
        ('not_pending', 'not_pending'),
    )
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="project_status", db_index=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="status_community", blank=True)
    seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.community} - {self.seen} - {self.status}"

    class Meta:
        indexes = [models.Index(fields=['project', 'community'])]
        verbose_name = 'Project Status'
        verbose_name_plural = 'Project Statuses'

class LabelNote(models.Model):
    bclabel = models.ForeignKey(BCLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="bclabel_note")
    tklabel = models.ForeignKey(TKLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="tklabel_note")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="note_sender", blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bclabel} - {self.tklabel} - {self.sender}"

    class Meta:
        indexes = [models.Index(fields=['bclabel', 'tklabel'])]
        verbose_name = 'Label Note'
        verbose_name_plural = 'Label Notes'

class LabelVersion(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="version_creator", blank=True)
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="version_approver", blank=True)
    bclabel = models.ForeignKey(BCLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="bclabel_version")
    tklabel = models.ForeignKey(TKLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="tklabel_version")
    version = models.SmallIntegerField(blank=True)
    version_text = models.TextField(blank=True)
    created = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.bclabel} - {self.tklabel} - {self.version}"
    
    class Meta:
        verbose_name = 'Label Version'
        verbose_name_plural = 'Label Versions'

class LabelTranslationVersion(models.Model):
    version_instance = models.ForeignKey(LabelVersion, null=True, blank=True, on_delete=models.CASCADE, related_name="label_version_translation")
    translated_name = models.CharField(max_length=150, blank=True)
    language_tag = models.CharField(max_length=5, blank=True)
    language = models.CharField(max_length=150, blank=True)
    translated_text = models.TextField(blank=True)
    created = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.version_instance}"
    
    class Meta:
        verbose_name = 'Label Translation Version'
        verbose_name_plural = 'Label Translation Versions'


class Connections(models.Model):
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE, blank=True,  related_name="community_connections", db_index=True)
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, related_name="institution_connections",  db_index=True)
    researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True, related_name="researcher_connections", db_index=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="communities_connected", db_index=True)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="institutions_connected", db_index=True)
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="researchers_connected", db_index=True)

    def __str__(self):
        return f"{self.community} - {self.institution} - {self.researcher}"

    class Meta:
        indexes = [models.Index(fields=['community', 'institution', 'researcher'])]
        verbose_name = 'Connections'
        verbose_name_plural = 'Connections'
