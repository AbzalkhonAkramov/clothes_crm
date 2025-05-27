from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import User, Translate, Article, Summary, Speechtotext, Project, PromoCodeUsage, PromoCode

from users.models import OrderPayment
from .models.related import SpeechtotextForBot
from .models.user import ChannelSubscribes


@admin.register(OrderPayment)
class OrderPaymentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'custom_amount', 'type', 'status', 'created_at', 'updated_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')

    def custom_amount(self, obj):
        return obj.amount / 100 if obj.type == OrderPayment.PaymentChoices.PAYME else obj.amount

    custom_amount.short_description = 'Amount'


@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': (
            'username', 'password', 'task_id', 'credit_sums', 'credit_seconds', 'used_sums',
            'used_seconds')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','phone', 'email', 'telegram_id', 'lang', 'device_token')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Login Info'), {'fields': ('date_joined', 'last_login', 'login_type')}),
    )
    list_display = ['username','phone', 'first_name', 'last_name', 'login_type', 'lang', 'is_staff']
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'login_type', 'lang')


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'user', 'action_type', 'output_type', 'created_at')
    search_fields = ('name', 'user__username', 'action_type')
    list_filter = ('action_type', 'output_type', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Speechtotext)
class SpeechtotextAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('project', 'user', 'file_name', 'created_at', 'updated_at')
    search_fields = ('project__name', 'user__username')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SpeechtotextForBot)
class SpeechtotextAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('voice_id', 'user', 'duration', 'created_at')


@admin.register(Summary)
class SummaryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('project', 'user', 'lang', 'created_at')
    search_fields = ('project__name', 'user__username', 'lang')
    list_filter = ('lang', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('project', 'user', 'lang', 'type', 'created_at')
    search_fields = ('project__name', 'user__username', 'lang', 'type')
    list_filter = ('lang', 'type', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Translate)
class TranslateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('project', 'user', 'lang', 'created_at')
    search_fields = ('project__name', 'user__username', 'lang')
    list_filter = ('lang', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(PromoCode)
class PromoCodeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = (
        'name', 'min_price', 'discount_amount', 'usage_limit', 'created_at', 'updated_at', 'active_status')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['activate_promo_codes', 'deactivate_promo_codes']

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">Inactive</span>')

    active_status.short_description = "Status"

    @admin.action(description="Activate selected promo codes")
    def activate_promo_codes(self, request, queryset):
        updated_count = queryset.update(is_active=True)
        self.message_user(request, f"{updated_count} promo codes were activated successfully.")

    @admin.action(description="Deactivate selected promo codes")
    def deactivate_promo_codes(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"{updated_count} promo codes were deactivated successfully.")


@admin.register(ChannelSubscribes)
class ChannelSubscribesAdmin(ImportExportModelAdmin):
    list_display = ('user', 'is_subscribe', 'created_at')
    list_filter = ('created_at', 'is_subscribe')
    search_fields = ('user__username',)
    ordering = ('-created_at',)


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'usage_count', 'created_at', 'updated_at')
    list_filter = ('promo_code__name', 'created_at', 'updated_at')
    search_fields = ('promo_code__name', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    # def has_add_permission(self, request):
    #     return False
