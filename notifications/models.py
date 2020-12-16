from django.db import models
from django.contrib.auth.models import User

class UserNotification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    viewed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title
