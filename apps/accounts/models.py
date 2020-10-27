from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from phone_field import PhoneField

class Role(models.Model):
    ADMIN = 1
    APPROVER = 2
    WRITER = 3
    EDITOR = 4
    IMPLEMENTOR = 5
    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (APPROVER, 'approver'),
        (WRITER, 'writer'),
        (EDITOR, 'editor'),
        (IMPLEMENTOR, 'implementor'),
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='photos/', blank=True)
    is_researcher = models.BooleanField(default=False)
    phone = PhoneField(blank=True, help_text='Contact phone number')
    nationality = models.CharField(verbose_name='nationality', max_length=60, blank=True)
    country = CountryField(blank=True)
    city_or_town = models.CharField(verbose_name='city or town', max_length=80, blank=True)
    job_title = models.CharField(verbose_name='job title', max_length=80, blank=True)
    affiliation = models.CharField(verbose_name='affiliation', max_length=60, blank=True)
    bio = models.TextField(verbose_name='bio', blank=True)
    community_member = models.BooleanField(default=False)


class Community(models.Model):
    community_name = models.CharField(max_length=80)
    community_code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)
    country = CountryField()
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.community_name

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'

class Institution(models.Model):
    institution_name = models.CharField(max_length=80)
    institution_code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)
    country = CountryField()
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.institution_name

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'

class UserCommunity(models.Model):
    name = models.CharField(max_length=10, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    communities = models.ManyToManyField(Community)
    roles = models.ManyToManyField(Role)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = 'User Communities'

class UserInstitution(models.Model):
    name = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    institution = models.ManyToManyField(Institution)
    roles = models.ManyToManyField(Role)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Institution'
        verbose_name_plural = 'User Institutions'

class Project(models.Model):
    who = models.TextField()
    when = models.TextField()
    where = models.TextField()
    what = models.TextField()
    abstract = models.TextField()
    target_species = models.TextField()

    def __str__(self):
        return self.who

