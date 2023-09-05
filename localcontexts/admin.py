import csv
import itertools, calendar
from datetime import datetime, timedelta, timezone
from django.db.models.functions import Extract, Concat
from django.db.models import Count, Q, Value, F, CharField, Case, When
from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext as _
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.apps import apps
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from accounts.models import Profile, UserAffiliation, SignUpInvitation
from accounts.utils import get_users_name
from rest_framework_api_key.admin import APIKey, APIKeyModelAdmin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group, User
from django.contrib.admin.widgets import AdminFileWidget
from bclabels.models import BCLabel
from communities.models import Community, InviteMember, JoinRequest
from helpers.models import *
from institutions.models import Institution
from researchers.utils import is_user_researcher
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

# FILTERS AND ADD-ONS
class AccountTypeFilter(admin.SimpleListFilter):
    title = 'Account Type'
    parameter_name = 'account'

    def lookups(self, request, model_admin):
        return [
            ('institution', 'Institution'),
            ('researcher', 'Researcher'),
            ('community', 'Community')
        ]
    
    def queryset(self, request, queryset):
        if self.value() == "institution":
            try:
                if queryset.model is ProjectAdmin:
                    qs = queryset.distinct().filter(project_creator_project__institution_id__isnull=False)
                else:
                    qs = queryset.distinct().filter(institution_id__isnull=False)
                return qs
            except:
                return queryset.none()
            
        elif self.value() == "researcher":
            try:
                if queryset.model is ProjectAdmin:
                    qs = queryset.distinct().filter(project_creator_project__researcher_id__isnull=False)
                else:
                    qs = queryset.distinct().filter(researcher_id__isnull=False)
                return qs
            except:
                return queryset.none()
        
        elif self.value() == "community":
            try:
                if queryset.model is ProjectAdmin:
                    qs = queryset.distinct().filter(project_creator_project__community_id__isnull=False)
                else:
                    qs = queryset.distinct().filter(community_id__isnull=False)
                return qs
            except:
                return queryset.none()
            
class PrivacyTypeFilter(admin.SimpleListFilter):
    title = 'Privacy Type'
    parameter_name = 'privacy'

    def lookups(self, request, model_admin):
        return [
            ('Public', 'Public'),
            ('Contributor', 'Contributor'),
            ('Private', 'Private')
        ]
    
    def queryset(self, request, queryset):
        privacy = self.value()
        try:
            if privacy != None:
                qs = queryset.distinct().filter(project_privacy=privacy)
                return qs
            else:
                return queryset
        except:
            return queryset.none()
        
class NoticeLabelFilter(admin.SimpleListFilter):
    title = 'Notice/Labels'
    parameter_name = 'notice_label'

    def lookups(self, request, model_admin):
        return [
            ('notices', 'Notices'),
            ('labels', 'Labels'),
            ('none', 'None')
        ]
    
    def queryset(self, request, queryset):
        try:
            if self.value() == 'notices':
                qs = queryset.distinct().filter(Q(project_notice__archived = False))
                return qs
            elif self.value() == 'labels':
                qs = queryset.distinct().filter(Q(bc_labels__isnull = False) | Q(tk_labels__isnull = False))
                return qs
            elif self.value() == 'none':
                qs = queryset.distinct().filter((Q(bc_labels__isnull = True) & Q(tk_labels__isnull = True)) &
            (Q(project_notice__archived__isnull = True) | Q(project_notice__archived = True)))
                return qs
            else:
                return queryset
        except:
            return queryset.none()
        
class HubActivityTypeFilter(admin.SimpleListFilter):
    title = 'Activity Type'
    parameter_name = 'activity_type'

    def lookups(self, request, model_admin):
        return [
            ('New Member Added', 'New Member Added'),
            ('New User', 'New User'),
            ('New Researcher', 'New Researcher'),
            ('New Community', 'New Community'),
            ('New Institution', 'New Institution'),
            ('Project Edited', 'Project Edited'),
            ('Project Created', 'Project Created'),
            ('Community Notified', 'Community Notified'),
            ('Label(s) Applied', 'Label(s) Applied'),
            ('Disclosure Notice(s) Added', 'Disclosure Notice(s) Added'),
            ('Engagement Notice Added', 'Engagement Notice Added'),
        ]
    
    def queryset(self, request, queryset):
        try:
            if self.value() == 'New Member Added':
                qs = queryset.distinct().filter(action_type = 'New Member Added')
                return qs
            elif self.value() == 'New User':
                qs = queryset.distinct().filter(action_type = 'New User')
                return qs
            elif self.value() == 'New Researcher':
                qs = queryset.distinct().filter(action_type = 'New Researcher')
                return qs
            elif self.value() == 'New Community':
                qs = queryset.distinct().filter(action_type = 'New Community')
                return qs
            elif self.value() == 'New Institution':
                qs = queryset.distinct().filter(action_type = 'New Institution')
                return qs
            elif self.value() == 'Project Edited':
                qs = queryset.distinct().filter(action_type = 'Project Edited')
                return qs
            elif self.value() == 'Project Created':
                qs = queryset.distinct().filter(action_type = 'Project Created')
                return qs
            elif self.value() == 'Community Notified':
                qs = queryset.distinct().filter(action_type = 'Community Notified')
                return qs
            elif self.value() == 'Label(s) Applied':
                qs = queryset.distinct().filter(action_type = 'Label(s) Applied')
                return qs
            elif self.value() == 'Disclosure Notice(s) Added':
                qs = queryset.distinct().filter(action_type = 'Disclosure Notice(s) Added')
                return qs
            elif self.value() == 'Engagement Notice Added':
                qs = queryset.distinct().filter(action_type = 'Engagement Notice Added')
                return qs
            else:
                return queryset
        except:
            return queryset.none()
        
class DateRangeFilter(admin.SimpleListFilter):
    title = 'Date Range'
    parameter_name = 'date_range'

    def choices(self, changelist):
        choices = list(super().choices(changelist))
        print(choices)
        choices[0]['display'] = _('last 30 Days')
        return [choices[2], choices[0], choices[1]]

    def lookups(self, request, model_admin):
        return [
            ('last 60 Days', 'last 60 Days'),
            ('all', _('All')),
        ]
    
    def queryset(self, request, queryset):
        try:
            if self.value() == 'last 30 Days' or self.value() is None:
                qs = queryset.distinct().filter(date__gte=(datetime.now(tz = timezone.utc) - timedelta(days = 30)))
                return qs
            elif self.value() == 'last 60 Days':
                qs = queryset.distinct().filter(date__gte=datetime.now(tz = timezone.utc) - timedelta(days = 60))
                return qs
            else:
                return queryset
        except:
            return queryset.none()

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <img style="width: 286px;height: 160.88px;object-fit: cover;" src="%s" alt="%s" width="200"/> %s ' % \
                (image_url, file_name, _('')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
    
class AdminAudioWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            audio_url = value.url
            file_name = str(value)
            output.append(u' <audio controls><source src="%s" type="audio/mpeg" alt="%s"> %s </audio>' % \
                (audio_url, file_name, _('')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
                
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta.verbose_name_plural)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

# CUSTOM ADMIN VIEWS
class Inactive(User):
    class Meta:
        proxy = True
        verbose_name = 'Inactive Account'
        verbose_name_plural = 'Inactive Accounts'
        app_label = 'admin'

class InactiveAccountsAdmin(admin.ModelAdmin):
    model = Inactive
    change_list_template = 'admin/change_lists/inactive_accounts_change_list.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        inactive_users = User.objects.filter(is_active = False, date_joined__lte = datetime.now(tz = timezone.utc) - timedelta(days = 30)).annotate(
            days_count = datetime.now(tz = timezone.utc) - F('date_joined'),
            account_name = F('username'),
            account_type = Value('User', output_field=CharField())
        ).values('id', 'account_name', 'days_count', 'account_type')

        researcher_created_projects = ProjectCreator.objects.filter(researcher__isnull = False).values_list('researcher_id')
        inactive_researchers = Researcher.objects.exclude(id__in = researcher_created_projects).filter(date_connected__lte = datetime.now(tz = timezone.utc) - timedelta(days = 90)).annotate(
            days_count = datetime.now(tz = timezone.utc) - F('date_connected'),
            account_name = Case(
                When(~Q(user__first_name="") & ~Q(user__last_name=""), 
                     then=Concat(F('user__first_name'), Value(' '), F('user__last_name'))),
                     default=F('user__username')
            ),
            account_type = Value('Researcher', output_field=CharField())
        ).values('id', 'account_name', 'days_count', 'account_type')

        inactive_institutions = Institution.objects.filter(is_approved = False, created__lte = datetime.now(tz = timezone.utc) - timedelta(days = 90)).annotate(
            days_count = datetime.now(tz = timezone.utc) - F('created'),
            account_name = F('institution_name'),
            account_type = Value('Institution', output_field=CharField())
        ).values('id', 'account_name', 'days_count', 'account_type')

        inactive_communities = Community.objects.filter(is_approved = False, created__lte = datetime.now(tz = timezone.utc) - timedelta(days = 90)).annotate(
            days_count = datetime.now(tz = timezone.utc) - F('created'),
            account_name = F('community_name'),
            account_type = Value('Community', output_field=CharField())
        ).values('id', 'account_name', 'days_count', 'account_type')
        
        # Combine and sort the data as needed
        results = sorted(list(itertools.chain(inactive_users, inactive_institutions, inactive_researchers, inactive_communities)), key = lambda k: k['days_count'])

        # Create custom pagination context
        pagination_context = {
            'results': results,
            'result_count': len(results)
        }

        response.context_data.update(**pagination_context)

        return response

admin_site.register(Inactive, InactiveAccountsAdmin)

class OTCLinks(OpenToCollaborateNoticeURL):
    class Meta:
        proxy = True
        verbose_name = 'Open to Collaborate Link'
        verbose_name_plural = 'Open to Collaborate Links'
        app_label = 'admin'

class OTCLinksAdmin(admin.ModelAdmin, ExportCsvMixin):
    model = OTCLinks
    list_display = ('name', 'view', 'added_by', 'datetime')
    search_fields = ('institution__institution_name', 'researcher__user__username', 'researcher__user__first_name', 'researcher__user__last_name', 'name')
    ordering = ('-added',)
    list_filter = (AccountTypeFilter, )
    actions = ['export_as_csv']
    
    def view(self, obj):
        project_url= obj.url
        return format_html('<a href="{}" target="_blank" title="View External Link">View</a>', project_url)
    view.short_description = "URL"
    
    def added_by(self, obj):
        if obj.institution_id:
            account_id = obj.institution_id
            account_url = 'institutions/institution'
            account_name = obj.institution.institution_name
        else:
            account_id = obj.researcher_id
            account_url = 'researchers/researcher'
            account_name = get_users_name(obj.researcher.user)
        
        return format_html('<a href="/admin/{}/{}/change/">{} </a>', account_url, account_id, account_name)
    
    def datetime(self, obj):
        added_date = obj.added.strftime('%m/%d/%Y %I:%M %p (%Z)').replace('AM', 'am').replace('PM', 'pm')
        return added_date
    
    datetime.short_description = "Date/Time"

admin_site.register(OTCLinks, OTCLinksAdmin)

class UserProfile(User):
    class Meta:
        proxy = True
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        app_label = 'admin'

class ProfileInline(admin.StackedInline):
    model = Profile
    readonly_fields = ('api_key',)
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    fields = (
        'profile_pic',
        ('city_town', 'state_province_region', 'country'),
        'position',
        'affiliation', 
        ('preferred_language', 'languages_spoken'),
        'is_researcher',
        'onboarding_on',
        'api_key'
    )

class UserAffiliationInline(admin.TabularInline):
    model = UserAffiliation
    max_num = 0

class UserProfileAdmin(UserAdmin, ExportCsvMixin):
    model = UserProfile
    list_display = ('profile_name', 'email', 'joined')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    ordering = ['-date_joined', 'username', 'first_name']
    actions = ['export_as_csv']
    inlines = [ProfileInline, UserAffiliationInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (('first_name', 'last_name'), 'email')}),
        (_('Permissions'), {
            'fields': (('is_active', 'is_staff', 'is_superuser'), 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': (('last_login', 'date_joined'),)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def profile_name(self, obj):
        name = get_users_name(obj)
        return name
    
    def joined(self, obj):
        date_joined = obj.date_joined.strftime('%m/%d/%Y %I:%M %p (%Z)').replace('AM', 'am').replace('PM', 'pm')
        return date_joined
    joined.admin_order_field = "date_joined"

admin_site.register(UserProfile, UserProfileAdmin)

class Labels(TKLabel):
    class Meta:
        proxy = True
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'
        app_label = 'admin'

class LabelDetailsAdmin(admin.ModelAdmin):
    model = Labels
    change_list_template = 'admin/change_lists/labels_change_list.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        label_details = {
            'tkattribution': {'name':'TK Attribution (TK A)', 'count': 0, 'type': 'attribution'},
            'tkclan': {'name':'TK Clan (TK CL)', 'count': 0, 'type': 'clan'},
            'tkfamily' : {'name':'TK Family (TK F)', 'count': 0, 'type': 'family'},
            'tktk_multiple_community' : {'name':'TK Multiple Communities (TK MC)', 'count': 0, 'type': 'tk_multiple_community'},
            'tkcommunity_voice' : {'name':'TK Community Voice (TK CV)', 'count': 0, 'type': 'community_voice'},
            'tkcreative' : {'name':'TK Creative (TK CR)', 'count': 0, 'type': 'creative'},
            'tkverified' : {'name':'TK Verified (TK V)', 'count': 0, 'type': 'verified'},
            'tknon_verified' : {'name':'TK Non-Verified (TK NV)', 'count': 0, 'type': 'non_verified'},
            'tkseasonal' : {'name':'TK Seasonal (TK S)', 'count': 0, 'type': 'seasonal'},
            'tkwomen_general' : {'name':'TK Women General (TK WG)', 'count': 0, 'type': 'women_general'},
            'tkmen_general' : {'name':'TK Men General (TK MG)', 'count': 0, 'type': 'men_general'},
            'tkmen_restricted' : {'name':'TK Men Restricted (TK MR)', 'count': 0, 'type': 'men_restricted'},
            'tkwomen_restricted' : {'name':'TK Women Restricted(TK WR)', 'count': 0, 'type': 'women_restricted'},
            'tkculturally_sensitive' : {'name':'TK Culturally Sensitive (TK CS)', 'count': 0, 'type': 'culturally_sensitive'},
            'tksecret_sacred' : {'name':'TK Secret/Sacred (TK SS)', 'count': 0, 'type': 'secret_sacred'},
            'tkcommercial' : {'name':'TK Open to Commercialization (TK OC)', 'count': 0, 'type': 'commercial'},
            'tknon_commercial' : {'name':'TK Non-Commercial (TK NC)', 'count': 0, 'type': 'non_commercial'},
            'tkcommunity_use_only' : {'name':'TK Community Use Only (TK CO)', 'count': 0, 'type': 'community_use_only'},
            'tkoutreach' : {'name':'TK Outreach (TK O)', 'count': 0, 'type': 'outreach'},
            'tkopen_to_collaboration' : {'name':'TK Open to collaboration', 'count': 0, 'type': 'open_to_collaboration'},

            'bcprovenance' : {'name':'BC Provenance (BC P)', 'count': 0, 'type': 'provenance'},
            'bcmultiple_community' : {'name':'BC Multiple Communities (BC MC)', 'count': 0, 'type': 'multiple_community'},
            'bcclan' : {'name':'BC Clan (BC CL)', 'count': 0, 'type': 'clan'},
            'bcconsent_verified' : {'name':'BC Consent Verified (BC CV)', 'count': 0, 'type': 'consent_verified'},
            'bcconsent_non_verified' : {'name':'BC Consent Non-Verified (BC CNV)', 'count': 0, 'type': 'consent_non_verified'},
            'bcresearch' : {'name':'BC Research Use (BC R)', 'count': 0, 'type': 'research'},
            'bccollaboration' : {'name':'BC Open to Collaboration (BC CB)', 'count': 0, 'type': 'collaboration'},
            'bccommercialization' : {'name':'BC Open to Commercialization (BC OC)', 'count': 0, 'type': 'commercialization'},
            'bcnon_commercial' : {'name':'BC Non-Commercial (BC NC)', 'count': 0, 'type': 'non_commercial'},
            'bcoutreach' : {'name':'BC Outreach (BC O)', 'count': 0, 'type': 'outreach'}
        }

        tk_labels = TKLabel.objects.values('label_type').annotate(
            label_count = Count('label_type'),
            label_name = Concat(Value('tk'), F('label_type'))
            ).values('label_name', 'label_count').order_by('label_name')
        bc_labels = BCLabel.objects.values('label_type').annotate(
            label_count = Count('label_type'),
            label_name = Concat(Value('bc'), F('label_type'))
            ).values('label_name', 'label_count').order_by('label_name')

        for label in tk_labels:
            label_details[label['label_name']]['count'] = label['label_count']
            label_details[label['label_name']]['class'] = 'tk'
        for label in bc_labels:
            label_details[label['label_name']]['count'] = label['label_count']
            label_details[label['label_name']]['class'] = 'bc'

        # Create custom pagination context
        pagination_context = {
            'results' : label_details,
            'result_count' : len(label_details)
        }

        response.context_data.update(**pagination_context)

        return response
    
class TKLabels(TKLabel):
    class Meta:
        proxy = True
        verbose_name = 'TK Label'
        verbose_name_plural = 'TK Labels'
        app_label = 'admin'

class BCLabels(BCLabel):
    class Meta:
        proxy = True
        verbose_name = 'BC Label'
        verbose_name_plural = 'BC Labels'
        app_label = 'admin'

class LabelVersionInline(admin.StackedInline):
    model = LabelVersion
    readonly_fields = ('version', 'version_text', 'created_by', 'approved_by', 'created', 'translation_versions')
    fields = ('version', 'created_by', 'version_text', 'is_approved', 'approved_by', 'created', 'translation_versions')
    extra=0
    max_num=0
    show_change_link = True
    classes = ['collapse']

    def translation_versions(self, obj):
        translation_versions = obj.label_version_translation.filter(version_instance=obj.id).count()
        return translation_versions
    translation_versions.short_description = 'Translation versions'

    def get_queryset(self, request):
        if isinstance(self.parent_obj, TKLabels):
            response = super(LabelVersionInline, self).get_queryset(request).filter(tklabel=self.parent_obj.id).select_related('created_by', 'approved_by', 'tklabel')
        elif isinstance(self.parent_obj, BCLabels):
            response = super(LabelVersionInline, self).get_queryset(request).filter(bclabel=self.parent_obj.id).select_related('created_by', 'approved_by', 'bclabel')
        return response
    
class LabelTranslationInline(admin.StackedInline):
    model = LabelTranslation
    fields = (
        'translated_name',
        ('language', 'language_tag'),
        'translated_text'
    )
    extra=0
    show_change_link = True
    classes = ['collapse']

    def get_queryset(self, request):
        if isinstance(self.parent_obj, TKLabels):
            response = super(LabelTranslationInline, self).get_queryset(request).filter(tklabel=self.parent_obj.id).select_related('tklabel')
        elif isinstance(self.parent_obj, BCLabels):
            response = super(LabelTranslationInline, self).get_queryset(request).filter(bclabel=self.parent_obj.id).select_related('bclabel')
        return response
 
class TKLabelAdmin(admin.ModelAdmin, ExportCsvMixin):
    model = TKLabels
    list_display = ('name', 'community', 'created_by', 'language', 'is_approved', 'created')
    search_fields = ('name', 'community__community_name', 'created_by__username', 'label_type')
    list_filter = ['is_approved']
    list_per_page = 15
    ordering = ['-created']
    actions = ['export_as_csv']

    readonly_fields = ('unique_id', 'created', 'version',)
    raw_id_fields = ('created_by', 'community', 'approved_by', 'last_edited_by')
    formfield_overrides = {models.FileField: {'widget': AdminAudioWidget}}
    
    def has_module_permission(self, request):
        return False

    def get_inlines(self, request, obj):
        inlines = []
        if obj.tklabel_translation.exists():
            inlines.append(LabelTranslationInline)  
        if obj.version:
            inlines.append(LabelVersionInline)
        return inlines
    
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline_instance in inline_instances:
            inline_instance.parent_obj = obj
        return inline_instances
    
    def get_fields(self, request, obj=None):
        fields = [
            'created_by',
            'label_type',
            'community',
            'name',
            ('language', 'language_tag'),
            'label_text',
            'audiofile',
            'img_url',
            'svg_url',
            'is_approved',
            'approved_by',
            'last_edited_by',
            'unique_id',
            'created'
        ]
        if obj.version:
            fields.append('version')
        return fields
    
class BCLabelAdmin(admin.ModelAdmin, ExportCsvMixin):
    model = BCLabels
    list_display = ('name', 'community', 'created_by', 'language', 'is_approved', 'created')
    search_fields = ('name', 'community__community_name', 'created_by__username', 'label_type')
    list_filter = ['is_approved']
    list_per_page = 15
    ordering = ['-created']
    actions = ['export_as_csv']

    readonly_fields = ('unique_id', 'created', 'version',)
    raw_id_fields = ('created_by', 'community', 'approved_by', 'last_edited_by')
    formfield_overrides = {models.FileField: {'widget': AdminAudioWidget}}
    
    def has_module_permission(self, request):
        return False

    def get_inlines(self, request, obj):
        inlines = []
        if obj.bclabel_translation.exists():
            inlines.append(LabelTranslationInline)  
        if obj.version:
            inlines.append(LabelVersionInline)
        return inlines
    
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline_instance in inline_instances:
            inline_instance.parent_obj = obj
        return inline_instances
    
    def get_fields(self, request, obj=None):
        fields = [
            'created_by',
            'label_type',
            'community',
            'name',
            ('language', 'language_tag'),
            'label_text',
            'audiofile',
            'img_url',
            'svg_url',
            'is_approved',
            'approved_by',
            'last_edited_by',
            'unique_id',
            'created'
        ]
        if obj.version:
            fields.append('version')
        return fields

admin_site.register(Labels, LabelDetailsAdmin)
admin_site.register(TKLabels, TKLabelAdmin)
admin_site.register(BCLabels, BCLabelAdmin)

class HubActivity(HubActivity):
    class Meta:
        proxy = True
        verbose_name = 'Hub Activity'
        verbose_name_plural = 'Hub Activity'
        app_label = 'admin'

class HubActivityAdmin(admin.ModelAdmin):
    list_display = ('action', 'action_type', 'date')
    list_per_page = 10
    list_filter = (DateRangeFilter, HubActivityTypeFilter,)
    ordering = ('-date',)

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def action(self, obj):
        user_name = get_users_name(User.objects.get(id=obj.action_user_id))

        if obj.action_account_type == 'institution':
            account_id = obj.institution_id
            account_name = Institution.objects.values_list('institution_name', flat=True).get(id=obj.institution_id)
            account_link = 'institutions/institution'
        elif obj.action_account_type == 'community':
            account_id = obj.community_id
            account_name = Community.objects.values_list('community_name', flat=True).get(id=obj.community_id)
            account_link = 'communities/community'
        elif obj.action_account_type == 'researcher' or obj.action_type == 'New Researcher':
            researcher = is_user_researcher(obj.action_user_id)
            account_id = researcher.id
            account_name = 'Researcher'
            account_link = 'researchers/researcher'
        
        if obj.project_id and obj.action_type != 'Engagement Notice Added':
            project = Project.objects.values_list('title', 'project_page').get(id=obj.project_id)
            project_name = project[0]
            project_url = project[1]
        elif obj.project_id and obj.action_type == 'Engagement Notice Added':
            project = OpenToCollaborateNoticeURL.objects.values_list('name', 'url').get(id=obj.project_id)
            project_name = project[0]
            project_url = project[1]
        
        if obj.action_type == 'New Member Added':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> joined <a href="/admin/{}/{}/change/">{}</a>', obj.action_user_id, user_name, account_link, account_id, account_name)

        elif obj.action_type == 'New User':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> has joined the Hub', obj.action_user_id, user_name)

        elif obj.action_type == 'New Researcher':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> has created a <a href="/admin/{}/{}/change/">Researcher</a> account', obj.action_user_id, user_name, account_link, account_id)

        elif obj.action_type == 'New Community':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> has created a Community account: <a href="/admin/{}/{}/change/">{}</a>', obj.action_user_id, user_name, account_link, account_id, account_name)

        elif obj.action_type == 'New Institution':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> has created an Institution account: <a href="/admin/{}/{}/change/">{}</a>', obj.action_user_id, user_name, account_link, account_id, account_name)

        elif obj.action_type == 'Project Edited':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) edited Project: {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)
        
        elif obj.action_type == 'Project Created':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) created Project: {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)

        elif obj.action_type == 'Community Notified':
            community_id = obj.community_id
            community_name = Community.objects.values_list('community_name', flat=True).get(id=obj.community_id)
            community_link = 'communities/community'
            action_message = format_html('<a href="/admin/{}/{}/change/">{}</a> was notified by <a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) of Project: {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', community_link, community_id, community_name, obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)

        elif obj.action_type == 'Label(s) Applied':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) applied Labels to Project: {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)

        elif obj.action_type == 'Disclosure Notice(s) Added':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) applied Notices to Project: {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)

        elif obj.action_type == 'Engagement Notice Added':
            action_message = format_html('<a href="/admin/admin/userprofile/{}/change/">{}</a> (<a href="/admin/{}/{}/change/">{}</a>) added an OTC Notice for {} <a href="/admin/projects/project/{}/change/" title="View Admin Page"><i class="fa-solid fa-user-gear"></i></a> | <a href="{}" target="_blank" title="View External Page"><i class="fa-solid fa-arrow-up-right-from-square fa-xs"></i></a>', obj.action_user_id, user_name, account_link, account_id, account_name, project_name, obj.project_id, project_url)

        return action_message
    action.short_description = "Action"
    
admin_site.register(HubActivity, HubActivityAdmin)

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
    search_fields = ('name', 'community__community_name', 'created_by__username', 'label_type')
    search_fields = ('name', 'community__community_name', 'created_by__username', 'label_type')

admin_site.register(TKLabel, TKLabelAdmin)