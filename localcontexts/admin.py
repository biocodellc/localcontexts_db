from django.contrib import admin
from django.utils.translation import gettext as _
from django.apps import apps
from django.template.response import TemplateResponse
from django.http import Http404
from django.shortcuts import render

from accounts.models import Profile, UserAffiliation, SignUpInvitation
from accounts.models import Profile, UserAffiliation, SignUpInvitation, User
from rest_framework_api_key.admin import APIKey, APIKeyModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from bclabels.models import BCLabel
from communities.models import Community, InviteMember, JoinRequest
from helpers.models import *
from institutions.models import Institution
from notifications.models import UserNotification, ActionNotification
from projects.models import *
from researchers.models import Researcher
from tklabels.models import TKLabel

# ADMIN HOMEPAGE
class MyAdminSite(admin.AdminSite):
    site_header = 'Local Contexts Hub Administration'
    index_title = 'Dashboard'
    site_title = 'Local Contexts Hub Admin'

    def index(self, request, context=None):
        otc_notices = OpenToCollaborateNoticeURL.objects.select_related('researcher', 'institution').all()

        reg_total = 0
        notices_total = 0

        bc_notice_count = 0
        tk_notice_count = 0
        attr_notice_count = 0
        otc_count = 0
        disclosure_count = 0

        community_count = 0
        institution_count = 0
        researcher_count = 0

        community_projects = 0
        institution_projects = 0
        researcher_projects = 0

        bclabels_count = 0
        tklabels_count = 0
        total_labels = 0

        project_Labels_count = 0
        project_inactivity_count = 0

        projects_count = 0

        # Registered accounts
        community_count = Community.objects.count() 
        institution_count = Institution.objects.count() 
        researcher_count = Researcher.objects.count()
        reg_total = community_count + institution_count + researcher_count

        # Notices
        bc_notice_count = Notice.objects.filter(notice_type="biocultural").count()
        tk_notice_count = Notice.objects.filter(notice_type="traditional_knowledge").count()
        attr_notice_count = Notice.objects.filter(notice_type="attribution_incomplete").count()
        otc_count = otc_notices.count()

        disclosure_count = bc_notice_count + tk_notice_count + attr_notice_count
        notices_total = bc_notice_count + tk_notice_count + attr_notice_count + otc_count
        

        for project in Project.objects.all():
            if project.has_labels():
                project_Labels_count += 1
            if project.has_labels() == False and project.has_notice() == False:
                project_inactivity_count += 1

        # How many projects were created by which account
        for project in ProjectCreator.objects.select_related('institution', 'community', 'researcher').all():
            if project.institution:
                institution_projects += 1
            if project.community:
                community_projects += 1
            if project.researcher:
                researcher_projects += 1

        projects_count = community_projects + institution_projects + researcher_projects

        # Labels
        bclabels_count = BCLabel.objects.count()
        tklabels_count = TKLabel.objects.count()
        total_labels = bclabels_count + tklabels_count

        # Chart Data
        accountData = {
            'labels': [
                'Community Accounts',
                'Insitution Accounts',
                'Researcher Accounts'
            ],
            'datasets': [{
                'data': [community_count, institution_count, researcher_count],
                'backgroundColor': [
                    'rgb(116, 181, 157)',
                    'rgb(242, 126, 48)',
                    'rgb(1, 117, 133)'
                ],
                'hoverOffset': 4
            }]
        }

        projectActivityData = {
            'labels': [
                'Engagement Notice',
                'Disclosure Notice',
                'Labels Applied',
                'No Labels/Notices'
            ],
            'datasets': [{
                'data': [disclosure_count, otc_count, project_Labels_count, project_inactivity_count],
                'backgroundColor': [
                    'rgb(116, 181, 157)',
                    'rgb(242, 126, 48)',
                    'rgb(1, 117, 133)',
                    'rgb(128,128,128)'
                ],
                'hoverOffset': 4
            }]
        }

        context = {
            'community_count': community_count,
            'researcher_count': researcher_count,
            'institution_count': institution_count,
            'reg_total': reg_total,

            'bc_notice_count': bc_notice_count,
            'tk_notice_count': tk_notice_count,
            'attr_notice_count': attr_notice_count,
            'notices_total': notices_total,

            'community_projects': community_projects,
            'institution_projects': institution_projects,
            'researcher_projects': researcher_projects,
            'projects_count': projects_count,

            'bclabels_count': bclabels_count,
            'tklabels_count': tklabels_count, 
            'total_labels': total_labels,

            'otc_notices': otc_notices,
            'otc_count' : otc_count,

            'accountData' : accountData,
            'projectActivityData' : projectActivityData
        }

        return super().index(request, context)
    
    # change the title of the page (the name that shows on the tab)
    def app_index(self, request, app_label, extra_context=None):
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])
        app_name = apps.get_app_config(app_label).verbose_name
        context = {
            **self.each_context(request),
            'title': _('%(app)s') % {'app': app_name},
            'app_list': [app_dict],
            'app_label': app_label,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context)

admin_site = MyAdminSite(name='lc-admin')

# ACCOUNTS ADMIN
class UserAdminCustom(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name',)

class SignUpInvitationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'date_sent')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'affiliation', 'is_researcher')
    readonly_fields = ('api_key',)

admin_site.register(Profile, ProfileAdmin)
admin_site.register(UserAffiliation)
admin_site.register(SignUpInvitation, SignUpInvitationAdmin)

# API KEYS ADMIN
admin_site.register(APIKey, APIKeyModelAdmin)

# AUTH ADMIN
class MyGroupAdmin(GroupAdmin):
    # Add customizations here, if needed
    pass

admin_site.register(User, UserAdminCustom)
admin_site.register(Group, MyGroupAdmin)

# BCLABELS ADMIN
class BCLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'language_tag', 'language', 'is_approved', 'created',)
    readonly_fields = ('unique_id', 'created', 'version',)
    search_fields = ('name', 'community__community_name', 'created_by__username',)

admin_site.register(BCLabel, BCLabelAdmin)

# COMMUNITIES ADMIN
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'community_creator', 'contact_name', 'contact_email', 'is_approved', 'created')
    search_fields = ('community_name', 'contact_name', 'contact_email',)
    readonly_fields = ('native_land_slug',)

class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('community', 'institution', 'user_from', 'user_to', 'status', 'date_sent')
    search_fields = ('community__community_name', 'institution__institution_name', 'user_from__username',)

class InviteMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'institution', 'sender', 'receiver', 'role', 'status', 'created')
    search_fields = ('community__community_name', 'institution__institution_name', 'sender__username', 'receiver__username',)

admin_site.register(Community, CommunityAdmin)
admin_site.register(InviteMember, InviteMemberAdmin)
admin_site.register(JoinRequest, JoinRequestAdmin)

# HELPERS ADMIN
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'notice_type', 'researcher', 'institution', 'created', 'archived' )
    search_fields = ('project__title', 'notice_type', 'researcher__user__username', 'institution__institution_name')

class OpenToCollaborateNoticeURLAdmin(admin.ModelAdmin):
    list_display = ('institution', 'researcher', 'name', 'url', 'added')
    search_fields = ('institution__institution_name', 'researcher__user__username', 'name', 'url')

class LabelTranslationAdmin(admin.ModelAdmin):
    list_display = ('translated_name', 'language', 'language_tag', 'translated_text', )

class EntitiesNotifiedAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project__title',)

class LabelVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'bclabel', 'tklabel', 'created', 'is_approved')
    readonly_fields = ('bclabel', 'tklabel', 'version', 'version_text', 'created_by', 'approved_by', 'created',)

class LabelTranslationVersionAdmin(admin.ModelAdmin):
    list_display = ('version_instance', 'translated_name', 'language', 'created')
    readonly_fields = ('version_instance', 'translated_name', 'language', 'language_tag', 'translated_text', 'created',)

class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'seen', 'status')
    search_fields = ('project__title', 'community__community_name')

# class ProjectCommentAdmin(admin.ModelAdmin):
#     list_display = ('project', 'sender', 'community', 'sender_affiliation', 'message', 'created')
#     search_fields = ('project',)

# class LabelNoteAdmin(admin.ModelAdmin):
#     list_display = ('bclabel', 'tklabel', 'sender',)

# admin.site.register(ProjectComment, ProjectCommentAdmin)
# admin.site.register(LabelNote, LabelNoteAdmin)
admin_site.register(ProjectStatus, ProjectStatusAdmin)
admin_site.register(Notice, NoticeAdmin)
admin_site.register(LabelVersion, LabelVersionAdmin)
admin_site.register(LabelTranslationVersion, LabelTranslationVersionAdmin)
admin_site.register(LabelTranslation, LabelTranslationAdmin)
admin_site.register(EntitiesNotified, EntitiesNotifiedAdmin)
admin_site.register(OpenToCollaborateNoticeURL, OpenToCollaborateNoticeURLAdmin)

# INSTITUTIONS ADMIN
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'institution_creator', 'contact_name', 'contact_email', 'is_approved', 'created')
    search_fields = ('institution_name', 'institution_creator__username', 'contact_name', 'contact_email',)

admin_site.register(Institution, InstitutionAdmin)

# NOTIFICAITONS ADMIN
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'community', 'notification_type', 'title', 'reference_id', 'created')

class ActionNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'community', 'institution', 'researcher', 'notification_type', 'title', 'created')

admin_site.register(UserNotification, UserNotificationAdmin)
admin_site.register(ActionNotification, ActionNotificationAdmin)

# PROJECTS ADMIN
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_creator', 'project_contact', 'project_contact_email', 'project_privacy', 'project_page', 'date_added', 'unique_id')
    readonly_fields = ('unique_id', 'project_page')
    search_fields = ('title', 'unique_id', 'project_creator__username', 'project_contact', 'project_contact_email',)

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project__title',)

class ProjectPersonAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'email')

class ProjectCreatorAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'institution', 'researcher')
    search_fields = ('project__title',)

class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'activity')    
    readonly_fields = ('project', 'date', 'activity')
    search_fields = ('project__title',)

class ProjectArchivedAdmin(admin.ModelAdmin):
    list_display = ('project_uuid', 'archived', 'community_id', 'institution_id', 'researcher_id')

class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ('project', 'community')

admin_site.register(Project, ProjectAdmin)
admin_site.register(ProjectContributors, ProjectContributorsAdmin)
admin_site.register(ProjectPerson, ProjectPersonAdmin)
admin_site.register(ProjectCreator, ProjectCreatorAdmin)
admin_site.register(ProjectActivity, ProjectActivityAdmin)
admin_site.register(ProjectArchived, ProjectArchivedAdmin)
admin_site.register(ProjectNote, ProjectNoteAdmin)

# RESEARCHERS ADMIN
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_email', 'orcid', 'primary_institution', 'date_connected')
    search_fields = ('contact_email', 'user__username', 'orcid', 'primary_institution', 'date_connected')
    readonly_fields = ('orcid_auth_token',)

admin_site.register(Researcher, ResearcherAdmin)

# TKLABELS ADMIN
class TKLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'language_tag', 'language', 'is_approved', 'created')
    readonly_fields = ('unique_id', 'created', 'version',)
    search_fields = ('name', 'community__community_name', 'created_by__username',)

admin_site.register(TKLabel, TKLabelAdmin)