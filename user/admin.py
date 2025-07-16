from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_number', 'name', 'email', 'role', 'photo', 'is_active', 'is_admin', 'is_superuser')
    list_filter = ('is_admin', 'is_active', 'is_superuser', 'role')

    fieldsets = (
        ('Personal info', {
            'fields': ('phone_number', 'password', 'name', 'email', 'photo', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_superuser')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'phone_number', 'name', 'email', 'photo', 'role', 'password1', 'password2', 'is_active', 'is_admin',
            'is_superuser'),
        }),
    )

    search_fields = ('phone_number', 'email', 'name')
    ordering = ('phone_number',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

