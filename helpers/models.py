from django.db import models
from django.contrib.auth.models import User
from bclabels.models import BCNotice, BCLabel
from tklabels.models import TKNotice, TKLabel
from communities.models import Community

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