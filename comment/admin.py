from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['owner', 'product', 'created_at', 'updated_at']
    list_filter = [ 'created_at', 'updated_at', 'product']
    search_fields = ['owner__name', 'owner__email', 'product__name', 'body']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    fieldsets = (
        ('Comment Info', {
            'fields': ('uid', 'owner', 'product', 'body')
        }),
        ('Rating & Timestamps', {
            'fields': ( 'created_at', 'updated_at')
        }),
    )
    date_hierarchy = 'created_at'
