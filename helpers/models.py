import json
import requests
from django.db import models
from django.contrib.auth.models import User
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from communities.models import Community
from researchers.models import Researcher
from institutions.models import Institution

class Notice(models.Model):
    TYPES = (
        ('biocultural', 'biocultural'),
        ('traditional_knowledge', 'traditional_knowledge'),
        ('attribution_incomplete', 'attribution_incomplete'),
    )
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE, related_name="project_notice", db_index=True)
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

    # Note: this will only work once the Notice itself is saved first, check the json file for what language tags are currently available.
    # Use: notice.save(language='fr')
    def set_translation(self, language_tag):
        with open('./localcontexts/static/json/NoticeTranslations.json') as json_file:
            translations_data = json.load(json_file)
            
        translation = None
        for item in translations_data:
            if item['noticeType'] == self.notice_type and item['languageTag'] == language_tag:
                translation = item['noticeDefaultText']
                break
        else:
            return

        NoticeTranslation.objects.update_or_create(
            notice=self,
            notice_type=self.notice_type,
            language_tag=item['languageTag'],
            language=item['language'],
            translated_name=item['noticeName'],
            translated_text=translation
        )

    def save(self, language_tag=None, *args, **kwargs):
        json_data = open('./localcontexts/static/json/Notices.json')
        data = json.load(json_data) #deserialize

        baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/'
        for item in data:
            if item['noticeType'] == self.notice_type:
                self.name = item['noticeName']
                self.img_url = baseURL + item['imgFileName']
                self.svg_url = baseURL + item['svgFileName']
                self.default_text = item['noticeDefaultText']
        
        if language_tag:
            self.set_translation(language_tag)

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.project.title)
    
    class Meta:
        indexes = [models.Index(fields=['project', 'researcher', 'institution'])]
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
        ordering = ('-created',)

class NoticeTranslation(models.Model):
    TYPES = (
        ('biocultural', 'biocultural'),
        ('traditional_knowledge', 'traditional_knowledge'),
        ('attribution_incomplete', 'attribution_incomplete'),
    )
    notice_type = models.CharField(max_length=50, null=True, choices=TYPES)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="notice_translations")
    language_tag = models.CharField(max_length=5, blank=True)
    language = models.CharField(max_length=150, blank=True)
    translated_name = models.CharField(max_length=150, blank=True)
    translated_text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.notice} - {self.language}"
    
    class Meta:
        verbose_name = 'Notice Translation'
        verbose_name_plural = 'Notice Translations'


class OpenToCollaborateNoticeURL(models.Model):
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, db_index=True, related_name="otc_institution_url")
    researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True, db_index=True, related_name="otc_researcher_url")
    name = models.CharField('Name of Website', max_length=250, null=True, blank=True)
    url = models.URLField('Link', null=True, unique=True)
    added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        indexes = [models.Index(fields=['institution', 'researcher'])]
        verbose_name = 'Open To Collaborate Notice URL'
        verbose_name_plural = 'Open To Collaborate Notice URLs'

class EntitiesNotified(models.Model):
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE, related_name="project_notified", db_index=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="communities_notified", db_index=True)
    institutions = models.ManyToManyField(Institution, blank=True, related_name="institutions_notified", db_index=True)
    researchers = models.ManyToManyField(Researcher, blank=True, related_name="researchers_notified", db_index=True)

    def is_user_in_notified_account(self, user):
        is_user_in_account = False
        for community in self.communities.all():
            if community.is_user_in_community(user):
                is_user_in_account = True
                break
        for institution in self.institutions.all():
            if institution.is_user_in_institution(user):
                is_user_in_account = True
                break
        for researcher in self.researchers.all():
            if user == researcher.user:
                is_user_in_account = True
                break
        return is_user_in_account

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
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE, related_name="project_comment", db_index=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="comment_community", blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="comment_sender", blank=True)
    sender_affiliation = models.CharField(max_length=350, blank=True)
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
        ('labels_applied', 'labels_applied'),
    )
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE, related_name="project_status", db_index=True)
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

class NoticeDownloadTracker(models.Model):
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="download_user", blank=True)
    collections_care_notices = models.BooleanField(default=False, null=True)
    open_to_collaborate_notice = models.BooleanField(default=False, null=True)
    date_downloaded = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.get_full_name()
    
    class Meta:
        verbose_name = 'Notice Download Tracker'
        verbose_name_plural = 'Notice Download Tracker'

class CollectionsCareNoticePolicy(models.Model):
    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True, db_index=True)
    policy_document = models.FileField(upload_to='institutions/support-files/collections-care-policies', blank=True, null=True)
    url = models.URLField('Website URL', null=True, blank=True, unique=True)
    added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.institution.institution_name)
    
    class Meta:
        verbose_name = 'Collections Care Notice Policy'
        verbose_name_plural = 'Collections Care Notice Policy'

class HubActivity(models.Model):
    TYPES = (
        ('New Member Added', 'New Member Added'),
        ('New User', 'New User'),
        ('New Researcher', 'New Researcher'),
        ('New Community', 'New Community'),
        ('New Institution', 'New Institution'),
        ('Project Edited', 'Project Edited'),
        ('Project Created', 'Project Created'),
        ('Community Notified', 'Community Notified'),
        ('Label(s) Applied', 'Label(s) Applied'),
        ('Disclosure Notice(s) Added', 'Disclosure Notice(s) Added'),
        ('Engagement Notice Added', 'Engagement Notice Added'),
    )

    action_user_id = models.IntegerField(null=True, blank=True)
    action_account_type = models.CharField(max_length=250, null=True, blank=True)
    community_id = models.IntegerField(null=True, blank=True)
    institution_id = models.IntegerField(null=True, blank=True)
    project_id = models.IntegerField(null=True, blank=True)
    action_type = models.CharField(max_length=30, null=True, choices=TYPES)
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Hub Activity'
        verbose_name_plural = 'Hub Activity'