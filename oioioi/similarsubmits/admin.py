from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from oioioi.contests.utils import is_contest_admin
from oioioi.similarsubmits.models import SubmissionsSimilarityGroup, \
    SubmissionsSimilarityEntry

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from oioioi.base import admin
from oioioi.base.utils import make_html_link
from oioioi.contests.admin import contest_site
from oioioi.contests.menu import contest_admin_menu_registry
from oioioi.contests.models import Submission


class SubmissionsSimilarityEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_link', 'submission_link',
            'submission_user_full_name', 'submission_problem_instance',
            'guilty']
    list_display_links = ['id', 'guilty']
    list_filter = ['guilty']
    search_fields = ['submission__user__username',
            'submission__user__last_name']
    raw_id_fields = ['submission', 'group']

    def has_add_permission(self, request):
        return is_contest_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_contest_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        return ['submission', 'group']

    def add_view(self, request, form_url='', extra_context=None):
        return redirect('bulk_add_similarities', contest_id=request.contest.id)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'submission':
            qs = Submission.objects.all()
            if request.contest:
                qs = qs.filter(problem_instance__contest=request.contest)
            kwargs['queryset'] = qs
        elif db_field.name == 'group':
            qs = SubmissionsSimilarityGroup.objects.all()
            if request.contest:
                qs = qs.filter(contest=request.contest)
            kwargs['queryset'] = qs
        return super(SubmissionsSimilarityEntryAdmin, self) \
            .formfield_for_foreignkey(db_field, request, **kwargs)

    def group_link(self, instance):
        return make_html_link(
            reverse('oioioiadmin:similarsubmits_'
                    'submissionssimilaritygroup_change',
            args=[instance.group_id]),
            instance.group_id)
    group_link.short_description = _("Group")

    def submission_link(self, instance):
        return make_html_link(reverse('submission',
            kwargs=dict(
                contest_id=instance.submission.problem_instance.contest_id,
                submission_id=instance.submission_id)),
            instance.submission_id)
    submission_link.short_description = _("Submission")

    def submission_user_full_name(self, instance):
        return instance.submission.user.get_full_name()
    submission_user_full_name.short_description = _("User name")
    submission_user_full_name.admin_order_field = 'submission__user__last_name'

    def submission_problem_instance(self, instance):
        if instance.submission.kind != 'NORMAL':
            return '%s (%s)' % (force_unicode(
                instance.submission.problem_instance),
                force_unicode(instance.submission.get_kind_display()))
        else:
            return instance.submission.problem_instance
    submission_problem_instance.short_description = _("Problem")
    submission_problem_instance.admin_order_field = \
        'submission__problem_instance'

    def get_list_select_related(self):
        return super(SubmissionsSimilarityEntryAdmin, self) \
                .get_list_select_related() + [
                    'submission', 'submission__user',
                    'submission__problem_instance'
                ]

    def queryset(self, request):
        queryset = super(SubmissionsSimilarityEntryAdmin, self) \
            .queryset(request)
        queryset = queryset.filter(
            submission__problem_instance__contest=request.contest)
        queryset = queryset.order_by('-id')
        return queryset

contest_site.contest_register(SubmissionsSimilarityEntry,
    SubmissionsSimilarityEntryAdmin)
contest_admin_menu_registry.register('submissions_similarity',
    _("Similar submits"), lambda request:
    reverse(
        'oioioiadmin:similarsubmits_submissionssimilarityentry_changelist'),
    order=100)


class SubmisionsSimilarityEntryInline(admin.TabularInline):
    model = SubmissionsSimilarityEntry
    extra = 0
    raw_id_fields = ['submission']

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'submission':
            qs = Submission.objects
            if request.contest:
                qs = qs.filter(problem_instance__contest=request.contest)
                kwargs['initial'] = request.contest
            kwargs['queryset'] = qs
        return super(SubmisionsSimilarityEntryInline, self) \
            .formfield_for_foreignkey(db_field, request, **kwargs)


class SubmissionsSimilarityGroupAdmin(admin.ModelAdmin):
    list_display = ['id']
    inlines = [SubmisionsSimilarityEntryInline]
    exclude = ['contest']

    def has_add_permission(self, request):
        return is_contest_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_contest_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        obj.contest = request.contest
        obj.save()

    def _interrupt_redirection(self, request):
        if 'came_from' not in request.GET and all(x not in request.POST
                for x in ('_continue', '_popup', '_saveasnew', '_addanother')):
            return True
        return False

    def response_add(self, request, obj, post_url_continue=None):
        if self._interrupt_redirection(request):
            return redirect('oioioiadmin:similarsubmits_'
                            'submissionssimilarityentry_changelist')
        return super(SubmissionsSimilarityGroupAdmin, self) \
            .response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if self._interrupt_redirection(request):
            return redirect('oioioiadmin:similarsubmits_'
                            'submissionssimilarityentry_changelist')
        return super(SubmissionsSimilarityGroupAdmin, self) \
            .response_change(request, obj)

    def response_delete(self, request):
        if self._interrupt_redirection(request):
            return redirect('oioioiadmin:similarsubmits_'
                            'submissionssimilarityentry_changelist')
        return super(SubmissionsSimilarityGroupAdmin, self) \
            .response_delete(request)

    def queryset(self, request):
        queryset = super(SubmissionsSimilarityGroupAdmin, self) \
            .queryset(request)
        queryset = queryset.filter(contest=request.contest)
        queryset = queryset.order_by('-id')
        return queryset

contest_site.contest_register(SubmissionsSimilarityGroup,
    SubmissionsSimilarityGroupAdmin)