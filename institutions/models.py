from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.core.validators import MaxLengthValidator
import uuid
import os

class ApprovedManager(models.Manager):
    def get_queryset(self):
        return super(ApprovedManager, self).get_queryset().filter(is_approved=True)

def get_file_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('institutions/support-files', filename)  

def institution_img_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('users/institution-images', filename)  

class Institution(models.Model):
    institution_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    institution_name = models.CharField(max_length=100, null=True, unique=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_email = models.EmailField(max_length=254, null=True, blank=True)
    image = models.ImageField(upload_to=institution_img_path, blank=True, null=True)
    support_document = models.FileField(upload_to=get_file_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True, validators=[MaxLengthValidator(200)])
    ror_id = models.CharField(max_length=80, blank=True, null=True)
    city_town = models.CharField(max_length=80, blank=True, null=True)
    state_province_region = models.CharField(verbose_name='state or province', max_length=100, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, related_name="institution_admins")
    editors = models.ManyToManyField(User, blank=True, related_name="institution_editors")
    viewers = models.ManyToManyField(User, blank=True, related_name="institution_viewers")
    is_approved = models.BooleanField(default=False, null=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="institution_approver")
    is_ror = models.BooleanField(default=True, null=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

    # Managers
    objects = models.Manager()
    approved = ApprovedManager()

    def get_location(self):
        components = [self.city_town, self.state_province_region, self.country]
        location = ', '.join(filter(None, components)) or 'None specified'
        return location

    def get_member_count(self):
        admins = self.admins.count()
        editors = self.editors.count()
        viewers = self.viewers.count()
        total_members = admins + editors + viewers + 1
        return total_members
    
    def get_admins(self):
        return self.admins.all()

    def get_editors(self):
        return self.editors.all()
    
    def get_viewers(self):
        return self.viewers.all()

    def is_user_in_institution(self, user):
        if user in self.viewers.all() or user in self.editors.all() or user in self.admins.all() or user == self.institution_creator:
            return True
        else:
            return False

    def get_distinct_creators(self):
        project_creators = self.institution_created_project.filter(institution=self).distinct("project__project_creator")
        return [element.project.project_creator for element in project_creators]

    def __str__(self):
        return str(self.institution_name)

    @property
    def institution_projects(self):
        institution_projects = self.institution_created_project.filter(institution=self)
        return institution_projects

    class Meta:
        indexes = [models.Index(fields=['id', 'institution_creator', 'image'])]
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
