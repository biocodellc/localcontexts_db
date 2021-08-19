from django.db import models
from django.contrib.auth.models import User
from bclabels.models import BCNotice, BCLabel
from tklabels.models import TKNotice, TKLabel
from communities.models import Community
from projects.models import Project
from researchers.models import Researcher
from institutions.models import Institution

class Notice(models.Model):
    TYPES = (
        ('biocultural', 'biocultural'),
        ('traditional_knowledge', 'traditional_knowledge')
    )
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE, related_name="project_notice")
    notice_type = models.CharField(max_length=50, null=True, choices=TYPES)
    communities = models.ManyToManyField(Community, blank=True, related_name="notice_communities")
    placed_by_researcher = models.ForeignKey(Researcher, null=True, on_delete=models.CASCADE, blank=True)
    placed_by_institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, blank=True)
    img_url = models.URLField(blank=True, null=True)
    default_text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.project.title)
    
    class Meta:
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
        ordering = ('-created',)

class LabelTranslation(models.Model):
    bclabel = models.ForeignKey(BCLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="bclabel_translation")
    tklabel = models.ForeignKey(TKLabel, null=True, blank=True, on_delete=models.CASCADE, related_name="tklabel_translation")
    title = models.CharField(max_length=150, blank=True)
    language = models.CharField(max_length=150, blank=True)
    translation = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Label Translation"
        verbose_name_plural = "Label Translations"

class NoticeComment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, null=True, related_name="notice_comment", blank=True)
    bcnotice = models.ForeignKey(BCNotice, on_delete=models.CASCADE, null=True, related_name="bcnotice_comment", blank=True)
    tknotice = models.ForeignKey(TKNotice, on_delete=models.CASCADE, null=True, related_name="tknotice_comment", blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="comment_community", blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="comment_sender", blank=True)
    message = models.TextField(max_length=1500, null=True, blank=True) #250 word limit on message
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return 'Comment {} by {}'.format(self.message, self.community)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('created',)

class NoticeStatus(models.Model):
    CHOICES = (
        ('pending', 'pending'),
        ('not_pending', 'not_pending'),
    )
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, null=True, related_name="notice_status", blank=True)
    bcnotice = models.ForeignKey(BCNotice, on_delete=models.CASCADE, null=True, related_name="bcnotice_status", blank=True)
    tknotice = models.ForeignKey(TKNotice, on_delete=models.CASCADE, null=True, related_name="tknotice_status", blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name="status_community", blank=True)
    seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.community} - {self.seen} - {self.status}"

    class Meta:
        verbose_name = 'Notice Status'
        verbose_name_plural = 'Notice Statuses'