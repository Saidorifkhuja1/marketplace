from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserLoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'uid',
        'name',
        'email',
        'telegram_id',
        'role',
        'is_active',
        'is_deleted',
        'created_at'
    )
    list_filter = ('role', 'is_active', 'is_deleted', 'is_admin', 'created_at')
    search_fields = ('name', 'username', 'email', 'telegram_id', 'phone_number')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'username', 'email')
        }),
        ('Telegram Info', {
            'fields': ('telegram_id', 'photo')
        }),
        ('Contact Info', {
            'fields': ('phone_number',)
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Status', {
            'fields': ('is_deleted', 'deleted_at')
        }),
        ('Important Dates', {
            'fields': ('created_at', 'updated_at', 'last_login', 'last_login_at')
        }),
    )

    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'name',
                'email',
                'password1',
                'password2',
                'telegram_id',
                'role',
                'is_active',
                'is_admin'
            ),
        }),
    )

    readonly_fields = ('uid', 'created_at', 'updated_at', 'deleted_at', 'last_login', 'last_login_at')

    filter_horizontal = ('groups', 'user_permissions')

    list_per_page = 25

    actions = ['activate_users', 'deactivate_users', 'soft_delete_users', 'restore_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) successfully activated.')

    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) successfully deactivated.')

    deactivate_users.short_description = "Deactivate selected users"

    def soft_delete_users(self, request, queryset):
        count = 0
        for user in queryset:
            user.soft_delete()
            count += 1
        self.message_user(request, f'{count} user(s) successfully soft deleted.')

    soft_delete_users.short_description = "Soft delete selected users"

    def restore_users(self, request, queryset):
        count = 0
        for user in queryset.filter(is_deleted=True):
            user.restore()
            count += 1
        self.message_user(request, f'{count} user(s) successfully restored.')

    restore_users.short_description = "Restore selected users"


@admin.register(UserLoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_email',
        'login_time',
        'ip_address',
        'success_status',
        'user_agent_short'
    )
    list_filter = ('success', 'login_time')
    search_fields = (
        'user__name',
        'user__email',
        'user__telegram_id',
        'ip_address'
    )
    ordering = ('-login_time',)
    readonly_fields = (
        'user',
        'login_time',
        'ip_address',
        'user_agent',
        'success'
    )

    list_per_page = 50

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def success_status(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Success</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Failed</span>'
            )

    success_status.short_description = 'Status'

    def user_agent_short(self, obj):
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'

    user_agent_short.short_description = 'User Agent'

    def has_add_permission(self, request):
        # Login history faqat avtomatik yaratiladi
        return False

    def has_change_permission(self, request, obj=None):
        # Login history o'zgartirib bo'lmaydi
        return False