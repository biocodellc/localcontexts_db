from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import Community, Institution, Account, UserCommunity, UserInstitution, Role


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username')
    read_only = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.
admin.site.register(Institution)
admin.site.register(Community)
admin.site.register(Account, AccountAdmin)
admin.site.register(UserCommunity)
admin.site.register(UserInstitution)
admin.site.register(Role)
