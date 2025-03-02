from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Category, Product, Order, OrderProduct, Comment

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'last_name', 'phone_number', 'lang_id', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number')
    list_filter = ('lang_id', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('chat_id', 'username', 'password')}),
        ('Personal Info', {'fields': ('lang_id', 'first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('chat_id', 'username', 'password1', 'password2', 'lang_id', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_superuser'),
        }),
    )
    ordering = ('chat_id',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'payment_type', 'created_at',)
    list_filter = ('status', 'payment_type')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'category', 'price',)
    list_filter = ("category", 'price')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'status',)
    list_filter = ('status',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Comment, CommentAdmin)