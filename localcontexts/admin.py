import itertools, calendar
from datetime import datetime, timedelta, timezone
from django.db.models.functions import Extract
from django.db.models import Count, Q
from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext as _
from django.apps import apps
from django.template.response import TemplateResponse
from django.http import Http404
from django.shortcuts import redirect, render

from accounts.models import Profile, UserAffiliation, SignUpInvitation
from rest_framework_api_key.admin import APIKey, APIKeyModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
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
    index_title = 'Home'
    site_title = 'Local Contexts Hub Admin'

    # add separate view urls not connected to a model
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('dashboard/',
                self.admin_view(self.dashboard_view), name = 'admin-dashboard')
        ]
        urls = my_urls + urls
        return urls
    
    def dashboard_view(self, request):
        if '_changedate' in request.POST:
            request.session['date'] = request.POST['filter-date']
            return redirect('lc-admin:admin-dashboard')
        elif '_resetdate' in request.POST:
            try:
                del request.session['date']
            except:
                pass
            return redirect('lc-admin:admin-dashboard')
        
        if 'date' in request.session:
            datestr = request.session['date']
            new_date = datetime.strptime(datestr, '%Y-%m-%dT%H:%M')
            new_date = new_date.astimezone(timezone.utc)
            end_date = new_date
        else:
            end_date = datetime.now(tz = timezone.utc)

        context = { 
            "app_list": self.get_app_list(request),
            **self.each_context(request),
            'date' : end_date
        }
        context.update(dashboardData(end_date))

        return render(request, 'admin/dashboard.html', context)
    
    # change the title of the page (the name that shows on the tab)
    def app_index(self, request, app_label, extra_context = None):
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key = lambda x: x['name'])
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

admin_site = MyAdminSite(name  = 'lc-admin')

# DASHBOARD VIEWS
def dashboardData(end_date):
    users = User.objects.filter(date_joined__lte = end_date)
    community = Community.objects.filter(created__lte = end_date)
    institution = Institution.objects.filter(created__lte = end_date)
    researcher = Researcher.objects.filter(date_connected__lte = end_date)
    bclabels = BCLabel.objects.filter(created__lte = end_date)
    tklabels = TKLabel.objects.filter(created__lte = end_date)
    projects = Project.objects.filter(date_added__lte = end_date)
    otc = OpenToCollaborateNoticeURL.objects.filter(added__lte=end_date)

    #Registered Users
    users_total = recent_users_count = 0
    users_total = users.count()
    recent_users_count = users.filter(date_joined__gte = end_date - timedelta(days = 30)).count()

    # Accounts by Country
    # FIXME: profile country saved as initials instead of full name. profile left out for now
    country_count = 0
    # users_by_country = Profile.objects.filter(country__isnull = False).distinct('country').values_list('country', flat = True)
    institutions_by_country = institution.filter(country__isnull = False).distinct('country').values_list('country', flat = True)
    communities_by_country = community.filter(country__isnull = False).distinct('country').values_list('country', flat = True)

    countries_list = list(itertools.chain(institutions_by_country, communities_by_country))
    country_count = len([*set(countries_list)])

    # Registered accounts
    community_count = institution_count = researcher_count = 0
    community_count = community.count() 
    institution_count = institution.count() 
    researcher_count = researcher.count()

    # Notices
    otc_count = 0
    otc_count = otc.count()

    # Labels
    bclabels_customized_count = bclabels_approved_count = bclabels_applied_count = 0
    tklabels_customized_count = tklabels_approved_count = tklabels_applied_count = 0
    
    bclabels_status = bclabels.aggregate(
        customized = Count('is_approved', filter = Q(is_approved = False)),approved = Count('is_approved', filter = (
            Q(is_approved = True) & Q(project_bclabels__isnull = True)
            )),
        applied = Count('id', filter = (
            Q(is_approved = True) & Q(project_bclabels__isnull = False)
        ), distinct = True)
    )
    bclabels_customized_count = bclabels_status['customized']
    bclabels_approved_count = bclabels_status['approved']
    bclabels_applied_count = bclabels_status['applied']

    tklabels_status = tklabels.aggregate(
       customized = Count('is_approved', filter = Q(is_approved = False)), approved = Count('is_approved', filter = (
            Q(is_approved = True) & Q(project_tklabels__isnull = True)
        )),
        applied = Count('id', filter = (
            Q(is_approved = True) & Q(project_tklabels__isnull = False)
        ), distinct = True)
    )
    tklabels_customized_count = tklabels_status['customized']
    tklabels_approved_count = tklabels_status['approved']
    tklabels_applied_count = tklabels_status['applied']

    # Projects
    project_labels_count = project_inactive_count = project_notices_count = projects_total_count = 0

    project_status = projects.aggregate(
        has_notice = Count('id', filter = Q(project_notice__archived = False), distinct = True),
        has_labels = Count('id', filter = (
            Q(bc_labels__isnull = False) | Q(tk_labels__isnull = False)
        ), distinct = True),
        inactive = Count('id', filter = (
            (Q(bc_labels__isnull = True) & Q(tk_labels__isnull = True)) &
            (Q(project_notice__archived__isnull = True) | Q(project_notice__archived = True))
        ), distinct = True),
    )

    project_notices_count = project_status['has_notice']
    project_labels_count = project_status['has_labels']
    project_inactive_count = project_status['inactive']
    projects_total_count = projects.count()

    chartData = {
        'accountData' : [community_count, institution_count, researcher_count],
        'projectActivityData' : [otc_count, project_notices_count, project_labels_count, project_inactive_count],
        'customizedLabelsData' : [tklabels_customized_count, tklabels_approved_count, tklabels_applied_count, bclabels_customized_count, bclabels_approved_count, bclabels_applied_count]
    }

    context = {
            'users_total' : users_total,
            'recent_users_count' : recent_users_count,
            'country_count' : country_count,
            'projects_count': projects_total_count
        }
    
    context.update(dataCharts(end_date, chartData))

    return context

def dataCharts(end_date, chartData):
    users = User.objects.filter(date_joined__lte = end_date)
    projects = Project.objects.filter(date_added__lte = end_date)

    # get last year by months (from today's date)
    lineChartData = {'user_count':{}, 'project_count':{}}
    lineChartMonths = []
    dateRange = end_date

    for i in range(1, 13):
        month = dateRange.month    
        year = dateRange.year
        month_year = " ".join([calendar.month_name[month], str(year)])
        lineChartMonths.append(month_year)
        lineChartData['user_count'][month_year] = 0
        lineChartData['project_count'][month_year] = 0
        dateRange -=  timedelta(days = calendar.monthrange(year, month)[1])

    lineChartMonths.reverse()
    lineChartData['user_count'] = dict(reversed(list(lineChartData['user_count'].items())))
    lineChartData['project_count'] = dict(reversed(list(lineChartData['project_count'].items())))

    # add user count based on month/year
    new_users = users.filter(date_joined__gte = (end_date - timedelta(days = 365))).annotate(month = Extract('date_joined', 'month'),year = Extract('date_joined', 'year')).values('month', 'year').annotate(c = Count('pk')).values('month', 'year', 'c').order_by('year', 'month')

    # add project count based on month/year
    new_projects = projects.filter(date_added__gte = (end_date - timedelta(days = 365))).annotate(month = Extract('date_added', 'month'),year = Extract('date_added', 'year')).values('month', 'year').annotate(c = Count('pk')).values('month', 'year', 'c').order_by('year', 'month')
    
    for user in new_users:
        user_month = user['month']
        user_month_year = " ".join([calendar.month_name[user_month], str(user['year'])])
        lineChartData['user_count'][user_month_year] = user['c']

    for project in new_projects:
        project_month = project['month']
        project_month_year = " ".join([calendar.month_name[project_month], str(project['year'])])
        lineChartData['project_count'][project_month_year] = project['c']

    new_users_counts = list(lineChartData['user_count'].values())
    new_project_counts = list(lineChartData['project_count'].values())

    # Colors
    teal_rgb, teal_hex = 'rgba(0, 115, 133, 1)', '#007385'
    light_teal_rgb, lighter_teal_rgb = 'rgba(43, 138, 153, 1)', 'rgba(85, 162, 174, 1)'
    orange_rgb, orange_hex = 'rgba(239, 108, 0, 1)', '#EF6C00'
    light_orange_rgb = 'rgba(242, 132, 43, 1)'
    lighter_orange_rgb = 'rgba(244, 157, 85, 1)'
    green_rgb, green_hex = 'rgba(16, 134, 112, 1)', '#108670'
    blue_rgb, blue_hex  = 'rgb(56, 119, 170)', '#3876aa'
    grey_rgb, grey_hex = 'rgba(100, 116, 139, 1)', '#64748B'

    # Pie Chart Data
    accountData = {
        'labels': ['Community', 'Insitution', 'Researcher'],
        'datasets': [{
            'data': chartData['accountData'],
            'backgroundColor': [green_rgb, orange_rgb,teal_rgb],
            'hoverOffset': 4
        }]
    }
    projectActivityData = {
        'labels': ['Engagement Notice', 'Disclosure Notice', 'Labels Applied', 'No Activity'],
        'datasets': [{
            'data': chartData['projectActivityData'],
            'backgroundColor': [orange_rgb,teal_rgb,green_rgb,grey_rgb],
            'hoverOffset': 4
        }]
    }
    customizedLabelsData = {
        'labels': ['Customized', 'Approved', 'Applied', 'Customized', 'Approved', 'Applied'],
        'datasets': [{
                'data': chartData['customizedLabelsData'],
                'backgroundColor': [lighter_orange_rgb, light_orange_rgb,orange_rgb, lighter_teal_rgb, light_teal_rgb,teal_rgb],
                'hoverOffset': 4
            }
        ]
    }
    
    # Line Chart Data
    newUsers = {
        'labels': lineChartMonths,
        'datasets': [
            {
                'data': new_users_counts,
                'label': 'New Users',
                'fill': 'false',
                'borderColor': orange_rgb,
                'tension':0.2
            },
            {
                'data': new_project_counts,
                'label': 'New Projects',
                'fill': 'false',
                'borderColor': blue_rgb,
                'tension':0.2
            }
        ]
    }
    
    context = {
        'accountData' : accountData,
        'projectActivityData' : projectActivityData,
        'customizedLabelsData' : customizedLabelsData,
        'newUsers' : newUsers,
    }
    
    return context

# ACCOUNTS ADMIN
class UserAdminCustom(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name',)

class SignUpInvitationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'date_sent')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'affiliation', 'is_researcher')
    readonly_fields = ('api_key',)

admin_site.register(Profile, ProfileAdmin)
admin_site.register(UserAffiliation)
admin_site.register(SignUpInvitation, SignUpInvitationAdmin)

# admin_site.unregister(User)
admin_site.register(User, UserAdminCustom)

# API KEYS ADMIN
admin_site.register(APIKey, APIKeyModelAdmin)

# AUTH ADMIN
class MyGroupAdmin(GroupAdmin):
    # Add customizations here, if needed
    pass

admin_site.register(Group, MyGroupAdmin)

# BCLABELS ADMIN
class BCLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'language_tag', 'language', 'is_approved', 'created',)
    readonly_fields = ('unique_id', 'created', 'version',)
    search_fields = ('name', 'community__community_name', 'created_by__username',)

admin_site.register(BCLabel, BCLabelAdmin)

# COMMUNITIES ADMIN
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'community_creator', 'contact_name', 'contact_email', 'is_approved', 'created', 'country')
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

class NoticeDownloadTrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'researcher', 'collections_care_notices', 'open_to_collaborate_notice', 'date_downloaded')
    search_fields = ('institution__institution_name', 'researcher__user', 'researcher__user__first_name', 'researcher__user__last_name', 'user', 'user__first_name', 'user__last_name')

class CollectionsCareNoticePolicyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'added')
    search_fields = ('institution__institution_name',)

class NoticeTranslationAdmin(admin.ModelAdmin):
    list_display = ('notice', 'notice_type', 'language')

admin_site.register(ProjectStatus, ProjectStatusAdmin)
admin_site.register(Notice, NoticeAdmin)
admin_site.register(LabelVersion, LabelVersionAdmin)
admin_site.register(LabelTranslationVersion, LabelTranslationVersionAdmin)
admin_site.register(LabelTranslation, LabelTranslationAdmin)
admin_site.register(EntitiesNotified, EntitiesNotifiedAdmin)
admin_site.register(OpenToCollaborateNoticeURL, OpenToCollaborateNoticeURLAdmin)
admin_site.register(NoticeDownloadTracker, NoticeDownloadTrackerAdmin)
admin_site.register(CollectionsCareNoticePolicy, CollectionsCareNoticePolicyAdmin)
admin_site.register(NoticeTranslation, NoticeTranslationAdmin)

# INSTITUTIONS ADMIN
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'institution_creator', 'contact_name', 'contact_email', 'is_approved', 'is_ror', 'created', 'country')
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