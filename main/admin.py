from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Announcement, User, Status, Image

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'phone', 'is_active', 'is_admin', 'is_staff')

    list_filter = ('is_active', 'is_admin')
    
    search_fields = ('email', 'phone')
    
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('phone',)}),
        ('Права доступа', {'fields': ('is_active', 'is_admin',)}),
        ('Важные даты', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ()

@admin.register(Status)
class AdminStatus(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_editable = ('name',)

@admin.register(Announcement)
class AdminAnnouncement(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'status', 'created_at', 'update_at',)
    list_filter = ('author', 'status',)
    
@admin.register(Image)
class AdminImage(admin.ModelAdmin):
    list_display = ('author', 'image', 'announcement', 'update_at', 'created_at',)
    list_filter = ('update_at', 'created_at',)