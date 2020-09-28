from django.db import models
from django.contrib.auth.models import User

class Community(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Community'
        verbose_name_plural = "Communities"

class Institution(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = "Institutions"


class UserProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=80)
    researcher = models.BooleanField()
    community_member = models.BooleanField()
    affiliation = models.CharField(max_length=80)
    bio = models.CharField(max_length=300)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.last_name, self.first_name)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = "User Profiles"

class UserInstitution(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    institution_id = models.ForeignKey(Institution, on_delete=models.CASCADE, default=None)
    admin = models.BooleanField()
    manager = models.BooleanField()
    governance = models.BooleanField()
    team = models.BooleanField()

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = 'User Institution'
        verbose_name_plural = "User Institutions"

# A way to track where a user is an admin, manger, board or member
class UserCommunity(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    community_id = models.ForeignKey(Community, on_delete=models.CASCADE, default=None)
    admin = models.BooleanField()
    manager = models.BooleanField()
    board = models.BooleanField()
    member = models.BooleanField()

    def __str__(self):
        return self.community_id

    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = "User Communities"