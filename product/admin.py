from django.contrib import admin
from .models import Product, Category

from django.contrib import admin
from .models import Product, Category, PendingProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'owner', 'created_at']
    list_filter = ['status', 'category']

@admin.register(PendingProduct)
class PendingProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'status', 'created_at']
    ordering = ['-created_at']
    actions = ['make_active']  # Action qo‘shildi

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='pending')

    def has_add_permission(self, request):
        return False  # qo‘lda qo‘shib bo‘lmaydi

    def has_change_permission(self, request, obj=None):
        return True   # o‘zgartirish mumkin

    def has_delete_permission(self, request, obj=None):
        return True   # o‘chirish mumkin

    # ==========================
    # CUSTOM ACTION
    # ==========================
    @admin.action(description="Mark selected products as Active")
    def make_active(self, request, queryset):
        updated_count = queryset.update(status='active')
        self.message_user(
            request,
            f"{updated_count} product(s) have been activated."
        )
# @admin.register(PendingProduct)
# class PendingProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'owner', 'category', 'created_at']
#     ordering = ['-created_at']
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(status='pending')
#
#     def has_add_permission(self, request):
#         return False  # qo‘lda qo‘shib bo‘lmaydi
#
#     def has_change_permission(self, request, obj=None):
#         return True   # o‘zgartirish mumkin
#
#     def has_delete_permission(self, request, obj=None):
#         return True   # o‘chirish mumkin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


