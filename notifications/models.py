from django.db import models
from django.contrib.auth.models import User
from communities.models import Community

class UserNotification(models.Model):
    TYPES = (
        ('welcome', 'welcome'),
        ('invitation', 'invitation'),
        ('request', 'request'),
        ('approval', 'approval'),
        ('accept', 'accept'),
        ('create', 'create'),
    )

    ROLES = (
        ('admin', 'admin'),
        ('editor', 'editor'),
        ('viewer', 'viewer'),
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

    def __str__(self):
        return f"{self.notification_type}-{self.title}"

    class Meta:
        verbose_name = 'User Notification'
        verbose_name_plural = 'User Notifications'

class CommunityNotification(models.Model):
    TYPES = (
        ('requests', 'Requests'),
        ('labels', 'Labels'),
        ('relationships', 'relationships'),
    )

    title = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=TYPES, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    reference_id = models.CharField(max_length=10, null=True, blank=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type}-{self.title}"

    class Meta:
        verbose_name = 'Community Notification'
        verbose_name_plural = 'Community Notifications'

