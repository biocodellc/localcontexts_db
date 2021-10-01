from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
import uuid
import os

def researcher_img_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('users/researcher-images', filename)  

class Researcher(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    orcid = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to=researcher_img_path, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    description = models.TextField(null=True, blank=True, validators=[MaxLengthValidator(200)])
    website = models.URLField(max_length=150, blank=True, null=True)
    primary_institution = models.CharField(max_length=250, null=True, blank=True)
    projects = models.ManyToManyField('projects.Project', blank=True, related_name="researcher_projects")
    orcid_auth_token = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user)
