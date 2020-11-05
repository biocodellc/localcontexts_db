from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    who = models.TextField()
    when = models.TextField()
    where = models.TextField()
    what = models.TextField()
    abstract = models.TextField()
    target_species = models.TextField()

    def __str__(self):
        return self.who

class Researcher(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    project = models.ManyToManyField(Project, blank=True)
