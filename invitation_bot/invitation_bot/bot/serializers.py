from rest_framework import serializers
from .models import Font, Template, Icon, TelegramUser, Invitation, UserSession


class FontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font
        fields = ['id', 'name', 'file', 'preview']


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'image', 'description', 'is_active',
            'width', 'height', 'text_area_x', 'text_area_y',
            'text_area_width', 'text_area_height', 'top_icon_x',
            'top_icon_y', 'bottom_icon_x', 'bottom_icon_y'
        ]


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = ['id', 'name', 'image', 'description', 'is_active']


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            'telegram_id', 'username', 'first_name', 'last_name',
            'language_code', 'is_active', 'created_at', 'last_activity'
        ]


class InvitationSerializer(serializers.ModelSerializer):
    template_details = TemplateSerializer(source='template', read_only=True)
    font_details = FontSerializer(source='font', read_only=True)
    top_icon_details = IconSerializer(source='top_icon', read_only=True)
    bottom_icon_details = IconSerializer(source='bottom_icon', read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id', 'user', 'name', 'template', 'template_details',
            'font', 'font_details', 'invitation_type', 'text_content',
            'text_color', 'font_size', 'top_icon', 'top_icon_details',
            'custom_top_image', 'bottom_icon', 'bottom_icon_details',
            'custom_bottom_image', 'final_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['final_image', 'created_at', 'updated_at']


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ['user', 'current_step', 'temp_data', 'current_invitation']