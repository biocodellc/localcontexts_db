from django.db import models
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution

class UserNotification(models.Model):
    TYPES = (
        ('Welcome', 'welcome'),
        ('Invitation', 'invitation'),
        ('Request', 'request'),
        ('Approval', 'approval'),
        ('Accept', 'accept'),
        ('Create', 'create'),
    )

    ROLES = (
        ('Admin', 'admin'),
        ('Editor', 'editor'),
        ('Viewer', 'viewer'),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="to_user")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="from_user")
    notification_type = models.CharField(max_length=10, choices=TYPES, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=8, choices=ROLES, null=True, blank=True)
    reference_id = models.CharField(max_length=20, null=True, blank=True)
    viewed = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.notification_type}-{self.title}"

    class Meta:
        verbose_name = 'User Notification'
        verbose_name_plural = 'User Notifications'
        ordering = ('-created',)

class CommunityNotification(models.Model):
    TYPES = (
        ('Labels', 'labels'),
        ('Connections', 'connections'),
        ('Activity', 'activity'),
        ('Projects', 'projects')
    )

    title = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=TYPES, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="community_noti_sender", blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True)
    reference_id = models.CharField(max_length=250, null=True, blank=True)
    viewed = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    class Meta:
        verbose_name = 'Community Notification'
        verbose_name_plural = 'Community Notifications'
        ordering = ('-created',)

class InstitutionNotification(models.Model):
    TYPES = (
        ('Requests', 'requests'),
        ('Labels', 'labels'),
        ('Connections', 'Connections'),
    )

    title = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=TYPES, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="institution_noti_sender", blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)
    reference_id = models.CharField(max_length=10, null=True, blank=True)
    viewed = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    class Meta:
        verbose_name = 'Institution Notification'
        verbose_name_plural = 'Institution Notifications'
        ordering = ('-created',)


