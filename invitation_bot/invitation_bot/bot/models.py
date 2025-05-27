from django.db import models
from django.utils.translation import gettext_lazy as _


class Font(models.Model):
    """Model for storing available fonts"""
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='fonts/')
    preview = models.ImageField(upload_to='fonts/previews/', null=True, blank=True)

    def __str__(self):
        return self.name


class Template(models.Model):
    """Model for invitation templates"""
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='templates/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Template dimensions
    width = models.PositiveIntegerField(default=1080)
    height = models.PositiveIntegerField(default=1920)

    # Default text areas and their positions
    text_area_x = models.PositiveIntegerField(default=540)  # Center X
    text_area_y = models.PositiveIntegerField(default=960)  # Center Y
    text_area_width = models.PositiveIntegerField(default=800)
    text_area_height = models.PositiveIntegerField(default=1200)

    # Default icon positions
    top_icon_x = models.PositiveIntegerField(default=540)
    top_icon_y = models.PositiveIntegerField(default=300)
    bottom_icon_x = models.PositiveIntegerField(default=540)
    bottom_icon_y = models.PositiveIntegerField(default=1600)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Icon(models.Model):
    """Model for predefined icons that can be used in invitations"""
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='icons/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    """Model to store Telegram user information"""
    telegram_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.username:
            return f"@{self.username}"
        return f"{self.first_name} {self.last_name or ''}"


class Invitation(models.Model):
    """Model for storing created invitations"""

    class InvitationType(models.TextChoices):
        WEDDING = 'WEDDING', _('Wedding')
        BIRTHDAY = 'BIRTHDAY', _('Birthday')
        PARTY = 'PARTY', _('Party')
        CORPORATE = 'CORPORATE', _('Corporate Event')
        OTHER = 'OTHER', _('Other')

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='invitations')
    name = models.CharField(max_length=200)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    font = models.ForeignKey(Font, on_delete=models.CASCADE)
    invitation_type = models.CharField(max_length=20, choices=InvitationType.choices, default=InvitationType.OTHER)

    # Text content and formatting
    text_content = models.TextField()
    text_color = models.CharField(max_length=7, default='#000000')  # HEX color code
    font_size = models.PositiveIntegerField(default=36)

    # Icons or images
    top_icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True, blank=True, related_name='top_invitations')
    custom_top_image = models.ImageField(upload_to='uploads/custom_icons/', null=True, blank=True)
    bottom_icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='bottom_invitations')
    custom_bottom_image = models.ImageField(upload_to='uploads/custom_icons/', null=True, blank=True)

    # Generated invitation image
    final_image = models.ImageField(upload_to='invitations/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.user}"


class UserSession(models.Model):
    """Model to store user session state for the Telegram bot"""
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name='session')
    current_step = models.CharField(max_length=50, blank=True)
    temp_data = models.JSONField(default=dict)
    current_invitation = models.ForeignKey(Invitation, on_delete=models.SET_NULL,
                                           null=True, blank=True, related_name='sessions')

    def __str__(self):
        return f"Session for {self.user}"