import os
import io
import requests
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from .models import TelegramUser, UserSession, Template, Font, Icon, Invitation


def get_or_create_user(user_data):
    """
    Get or create a TelegramUser from Telegram user data

    Args:
        user_data: Telegram user data dictionary

    Returns:
        TelegramUser: User object
    """
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=user_data.id,
        defaults={
            'username': user_data.username,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'language_code': getattr(user_data, 'language_code', None),
        }
    )

    # Update user information if it has changed
    if not created:
        updated = False
        if user.username != user_data.username:
            user.username = user_data.username
            updated = True
        if user.first_name != user_data.first_name:
            user.first_name = user_data.first_name
            updated = True
        if user.last_name != user_data.last_name:
            user.last_name = user_data.last_name
            updated = True

        if updated:
            user.save()

    return user


def get_or_create_session(user):
    """
    Get or create a user session

    Args:
        user: TelegramUser object

    Returns:
        UserSession: Session object
    """
    session, created = UserSession.objects.get_or_create(
        user=user,
        defaults={
            'current_step': 'start',
            'temp_data': {},
        }
    )
    return session


def download_telegram_file(file_id, bot):
    """
    Download a file from Telegram

    Args:
        file_id: Telegram file ID
        bot: Telegram bot instance

    Returns:
        bytes: File content as bytes
    """
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
    response = requests.get(file_url)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download file: {response.status_code}")


def save_uploaded_image(file_bytes, file_name, folder='uploads'):
    """
    Save an uploaded image and return a Django ContentFile

    Args:
        file_bytes: File content as bytes
        file_name: Original file name
        folder: Destination folder

    Returns:
        ContentFile: Django ContentFile object
    """
    # Process image to ensure it's valid and optimize it
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img_io = io.BytesIO()

        # Preserve transparency if PNG
        if file_name.lower().endswith('.png'):
            img = img.convert('RGBA')
            img.save(img_io, format='PNG', optimize=True)
        else:
            img = img.convert('RGB')
            img.save(img_io, format='JPEG', optimize=True, quality=85)

        img_io.seek(0)
        return ContentFile(img_io.getvalue(), name=file_name)

    except Exception as e:
        raise Exception(f"Invalid image file: {str(e)}")


def get_active_templates():
    """Get list of active templates as (id, name) tuples"""
    return list(Template.objects.filter(is_active=True).values_list('id', 'name'))


def get_fonts():
    """Get list of fonts as (id, name) tuples"""
    return list(Font.objects.all().values_list('id', 'name'))


def get_icons():
    """Get list of icons as (id, name) tuples"""
    return list(Icon.objects.filter(is_active=True).values_list('id', 'name'))


def get_invitation_types():
    """Get list of invitation types"""
    return [(choice.value, choice.label) for choice in Invitation.InvitationType]