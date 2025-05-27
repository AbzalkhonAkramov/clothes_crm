from django.contrib import admin
from .models import Font, Template, Icon, TelegramUser, Invitation, UserSession

@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'preview']
    search_fields = ['name']

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'description', 'is_active')
        }),
        ('Dimensions', {
            'fields': ('width', 'height')
        }),
        ('Text Area Position', {
            'fields': ('text_area_x', 'text_area_y', 'text_area_width', 'text_area_height')
        }),
        ('Icon Positions', {
            'fields': ('top_icon_x', 'top_icon_y', 'bottom_icon_x', 'bottom_icon_y')
        }),
    )

@admin.register(Icon)
class IconAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'created_at', 'last_activity']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['telegram_id', 'username', 'first_name', 'last_name', 'language_code', 'created_at', 'last_activity']

class UserSessionInline(admin.TabularInline):
    model = UserSession
    can_delete = False
    readonly_fields = ['current_step', 'temp_data', 'current_invitation']
    extra = 0

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'invitation_type', 'template', 'created_at']
    list_filter = ['invitation_type', 'created_at', 'template', 'font']
    search_fields = ['name', 'user__username', 'user__first_name', 'text_content']
    readonly_fields = ['final_image', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'invitation_type', 'template', 'font')
        }),
        ('Text Settings', {
            'fields': ('text_content', 'text_color', 'font_size')
        }),
        ('Icons and Images', {
            'fields': ('top_icon', 'custom_top_image', 'bottom_icon', 'custom_bottom_image')
        }),
        ('Generated Invitation', {
            'fields': ('final_image', 'created_at', 'updated_at')
        }),
    )

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_step', 'current_invitation']
    search_fields = ['user__username', 'user__first_name', 'current_step']
    readonly_fields = ['user', 'current_step', 'temp_data', 'current_invitation']