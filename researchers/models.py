from django.db import models
from django.contrib.auth.models import User
# from communities.models import Community
# from institutions.models import Institution
# from projects.models import Project

class Researcher(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    orcid = models.CharField(max_length=19, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    # projects = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return str(self.user)

# class ProjectContributors(models.Model):
#     project = models.OneToOneField(Project, null=True, on_delete=models.CASCADE)
#     community = models.ForeignKey(Community, null=True, blank=True, on_delete=models.DO_NOTHING)
#     institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.DO_NOTHING)

#     def __str__(self):
#         return str(self.project)

#     class Meta:
#         verbose_name = 'Project Contributors'
#         verbose_name_plural = 'Project Contributors'
