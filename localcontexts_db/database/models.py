from django.db import models

class Users(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=80)
    affiliation = models.CharField(max_length=80)
    bio = models.CharField(max_length=150)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class UserInstitution(models.Model):
    users_id = models.IntegerField()
    institution_id = models.CharField(max_length=100)
    admin = models.BooleanField()
    manager = models.BooleanField()
    governance = models.BooleanField()
    team = models.BooleanField()

class UserCommunity(models.Model):
    users_id = models.IntegerField()
    institution_id = models.CharField(max_length=100) 
    admin = models.BooleanField()
    manager = models.BooleanField()
    board = models.BooleanField()
    member = models.BooleanField()

class Institutions(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)

class Community(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    contact_name = models.CharField(max_length=80)
    contact_email = models.EmailField(max_length=254)

