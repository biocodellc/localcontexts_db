from django.db import models
from django.contrib.auth.models import User

class Researcher(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    orcid = models.CharField(max_length=19, null=True)
    image = models.ImageField(upload_to='users/researcher-images', blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(max_length=150, blank=True, null=True)

    def __str__(self):
        return str(self.user)
