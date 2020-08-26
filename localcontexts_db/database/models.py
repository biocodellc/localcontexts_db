from django.db import models

class Users(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.CharField(max_length=80)
    phone = models.CharField(max_length=80)
    affiliation = models.CharField(max_length=80)
    bio = models.CharField(max_length=150)
    # date_created = 
    # date_modified =

class UserInstitution(models.Model):
    users_id = models.IntegerField()
    # institution_id =
    admin = models.BooleanField()
    manager = models.BooleanField()
    # governance = 
    # team =

class UserCommunity(models.Model):
    users_id = models.IntegerField()
    # institution_id = 
    admin = models.BooleanField()
    manager = models.BooleanField()
    board = models.BooleanField()
    # member =

class Institutions(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.CharField(max_length=80)

class Community(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.CharField(max_length=80)

