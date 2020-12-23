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
    title = models.CharField(max_length=200)
    message = models.TextField()
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="to_user")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="from_user")
    notification_type = models.CharField(max_length=10, choices=TYPES, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    # reference_id = models.CharField(max_length=20, null=True, blank=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type}-{self.title}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

