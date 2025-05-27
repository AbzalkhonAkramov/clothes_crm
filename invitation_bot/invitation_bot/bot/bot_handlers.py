import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse
from django.db import transaction

from .models import TelegramUser, UserSession, Template, Font, Icon, Invitation
from .utils import (
    get_or_create_user, get_or_create_session, download_telegram_file,
    save_uploaded_image, get_active_templates, get_fonts, get_icons,
    get_invitation_types
)
from .services import generate_invitation_image

logger = logging.getLogger(__name__)

# Define conversation states
(
    START, MAIN_MENU, CREATE_INVITATION,
    SELECT_TEMPLATE, SELECT_FONT, ENTER_TEXT, CHOOSE_TEXT_COLOR,
    SELECT_TOP_ICON, UPLOAD_TOP_IMAGE, SELECT_BOTTOM_ICON, UPLOAD_BOTTOM_IMAGE,
    GENERATE_PREVIEW, SAVE_INVITATION, VIEW_INVITATIONS, INVITATION_DETAIL,
    HELP
) = range(16)

# Define flow for creating an invitation
CREATION_FLOW = [
    SELECT_TEMPLATE, SELECT_FONT, ENTER_TEXT, CHOOSE_TEXT_COLOR,
    SELECT_TOP_ICON, SELECT_BOTTOM_ICON, GENERATE_PREVIEW, SAVE_INVITATION
]


# Helper functions for buttons
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("🎨 Create New Invitation")],
        [KeyboardButton("📂 My Invitations"), KeyboardButton("ℹ️ Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_yes_no_keyboard(callback_prefix):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"{callback_prefix}_yes"),
            InlineKeyboardButton("No", callback_data=f"{callback_prefix}_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_back_keyboard(callback_prefix):
    keyboard = [
        [
            InlineKeyboardButton("Skip", callback_data=f"{callback_prefix}_skip"),
            InlineKeyboardButton("Back", callback_data=f"{callback_prefix}_back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_items_keyboard(items, callback_prefix, page=0, items_per_page=5):
    """Generate a keyboard with pagination for a list of items"""
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Slice items for current page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_items = items[start_idx:end_idx]

    keyboard = []
    # Create buttons for each item
    for item_id, item_name in current_items:
        keyboard.append([InlineKeyboardButton(
            item_name, callback_data=f"{callback_prefix}_{item_id}"
        )])

    # Add navigation buttons if needed
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "⬅️ Previous", callback_data=f"{callback_prefix}_page_{page - 1}"
        ))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            "Next ➡️", callback_data=f"{callback_prefix}_page_{page + 1}"
        ))

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Add back button
    keyboard.append([InlineKeyboardButton(
        "Back", callback_data=f"{callback_prefix}_back"
    )])

    return InlineKeyboardMarkup(keyboard)


def get_color_keyboard():
    """Generate a keyboard with color options"""
    colors = [
        ["#000000", "Black"], ["#FFFFFF", "White"], ["#FF0000", "Red"],
        ["#00FF00", "Green"], ["#0000FF", "Blue"], ["#FFFF00", "Yellow"],
        ["#FF00FF", "Magenta"], ["#00FFFF", "Cyan"], ["#FFA500", "Orange"],
        ["#800080", "Purple"], ["#008000", "Dark Green"], ["#800000", "Maroon"]
    ]

    keyboard = []
    for i in range(0, len(colors), 3):
        row = []
        for j in range(3):
            if i + j < len(colors):
                color_code, color_name = colors[i + j]
                row.append(InlineKeyboardButton(
                    color_name, callback_data=f"color_{color_code}"
                ))
        keyboard.append(row)

    # Add back button
    keyboard.append([InlineKeyboardButton(
        "Back", callback_data="color_back"
    )])

    return InlineKeyboardMarkup(keyboard)


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and send welcome message"""
    user_data = update.effective_user

    # Store user in database
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)
    session.current_step = 'start'
    session.save()

    # Welcome message
    await update.message.reply_text(
        f"Hello, {user.first_name}! 👋\n\n"
        "Welcome to the Invitation Maker Bot! I can help you create beautiful invitation images "
        "for weddings, parties, and other events.\n\n"
        "What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )

    return MAIN_MENU


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    await update.message.reply_text(
        "🤖 *Invitation Maker Bot Help* 🤖\n\n"
        "This bot helps you create beautiful invitation images for your events.\n\n"
        "*Main Features:*\n"
        "• Create custom invitations\n"
        "• Choose from different templates\n"
        "• Select fonts and colors\n"
        "• Add decorative icons\n"
        "• Save and reuse your invitations\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "To get started, just tap the 'Create New Invitation' button from the main menu!",
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu options"""
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    message = update.message.text.strip()

    if message == "🎨 Create New Invitation":
        # Clear any previous session data related to creation
        session.temp_data = {}
        session.current_invitation = None
        session.current_step = 'create_invitation'
        session.save()

        await update.message.reply_text(
            "Let's create a new invitation! 🎨\n\n"
            "First, what type of invitation are you creating?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(name, callback_data=f"type_{code}")]
                for code, name in get_invitation_types()
            ])
        )
        return CREATE_INVITATION

    elif message == "📂 My Invitations":
        # Get user's invitations
        invitations = Invitation.objects.filter(user=user).order_by('-created_at')

        if not invitations.exists():
            await update.message.reply_text(
                "You haven't created any invitations yet.\n\n"
                "Tap 'Create New Invitation' to get started!",
                reply_markup=get_main_menu_keyboard()
            )
            return MAIN_MENU

        # Create a list of invitations for the keyboard
        invitation_list = [(inv.id, inv.name) for inv in invitations]

        await update.message.reply_text(
            "Here are your saved invitations:",
            reply_markup=get_items_keyboard(invitation_list, "invitation")
        )
        return VIEW_INVITATIONS

    elif message == "ℹ️ Help":
        return await help_command(update, context)

    else:
        await update.message.reply_text(
            "Please use the menu buttons to navigate.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU


# Callback query handler functions
async def invitation_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle selection of invitation type"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Extract the invitation type from callback data
    invitation_type = query.data.replace("type_", "")

    # Store the invitation type in the session
    session.temp_data['invitation_type'] = invitation_type
    session.current_step = 'select_template'
    session.save()

    # Ask user to name the invitation
    await query.message.reply_text(
        "Great! Please enter a name for your invitation:"
    )
    return SELECT_TEMPLATE


async def process_invitation_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the invitation name entered by the user"""
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Get the invitation name from the message
    invitation_name = update.message.text.strip()

    # Store the invitation name in the session
    session.temp_data['invitation_name'] = invitation_name
    session.save()

    # Show available templates
    templates = get_active_templates()

    await update.message.reply_text(
        "Please select a template for your invitation:",
        reply_markup=get_items_keyboard(templates, "template")
    )
    return SELECT_TEMPLATE


async def template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle template selection"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    # Handle pagination
    if callback_data.startswith("template_page_"):
        page = int(callback_data.replace("template_page_", ""))
        templates = get_active_templates()
        await query.edit_message_text(
            "How would you like to add a bottom icon?",
            reply_markup=InlineKeyboardMarkup(options_keyboard)
        )
        return SELECT_BOTTOM_ICON

    elif callback_data == "bottom_icon_library":
        # Show available icons
        icons = get_icons()

        await query.message.reply_text(
            "Please select an icon:",
            reply_markup=get_items_keyboard(icons, "bottom_icon_select")
        )
        return SELECT_BOTTOM_ICON

    elif callback_data == "bottom_icon_select_back":
        # Go back to icon options
        options_keyboard = [
            [InlineKeyboardButton("Select from library", callback_data="bottom_icon_library")],
            [InlineKeyboardButton("Upload my own", callback_data="bottom_icon_upload")],
            [InlineKeyboardButton("Back", callback_data="bottom_icon_back")]
        ]

        await query.edit_message_text(
            "How would you like to add a bottom icon?",
            reply_markup=InlineKeyboardMarkup(options_keyboard)
        )
        return SELECT_BOTTOM_ICON

    elif callback_data.startswith("bottom_icon_select_page_"):
        # Handle pagination for icons
        page = int(callback_data.replace("bottom_icon_select_page_", ""))
        icons = get_icons()

        await query.edit_message_text(
            "Please select an icon:",
            reply_markup=get_items_keyboard(icons, "bottom_icon_select", page=page)
        )
        return SELECT_BOTTOM_ICON

    elif callback_data.startswith("bottom_icon_select_"):
        # Handle icon selection
        icon_id = int(callback_data.replace("bottom_icon_select_", ""))

        # Store icon in session
        session.temp_data['bottom_icon_id'] = icon_id
        session.save()

        # Show selected icon
        icon = Icon.objects.get(id=icon_id)
        await query.message.reply_photo(
            photo=open(icon.image.path, 'rb'),
            caption=f"Selected bottom icon: {icon.name}"
        )

        # Move to preview generation
        await generate_preview(update, context)
        return GENERATE_PREVIEW

    elif callback_data == "bottom_icon_upload":
        # Prompt user to upload image
        await query.message.reply_text(
            "Please upload an image to use as the bottom icon.\n\n"
            "For best results, use a PNG image with transparency, ideally less than 500x500 pixels."
        )
        return UPLOAD_BOTTOM_IMAGE

    elif callback_data == "bottom_icon_back":
        # Go back to top icon selection
        await query.message.reply_text(
            "Would you like to add an icon at the top of your invitation?",
            reply_markup=get_yes_no_keyboard("top_icon")
        )
        return SELECT_TOP_ICON

    elif callback_data == "bottom_icon_no":
        # Skip bottom icon, move to preview
        session.temp_data['bottom_icon_id'] = None
        session.temp_data['custom_bottom_image'] = None
        session.save()

        # Generate preview
        await generate_preview(update, context)
        return GENERATE_PREVIEW

    return SELECT_BOTTOM_ICON


async def process_bottom_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process uploaded bottom image"""
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Check if a photo was uploaded
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "Please upload an image file.",
            reply_markup=get_skip_back_keyboard("bottom_icon_upload")
        )
        return UPLOAD_BOTTOM_IMAGE

    try:
        if update.message.photo:
            # Get the largest photo size
            file_id = update.message.photo[-1].file_id
            file_name = f"user_upload_{user.telegram_id}_bottom.jpg"
        else:
            # Handle document upload
            document = update.message.document
            if not document.mime_type.startswith('image/'):
                raise Exception("Please upload an image file.")

            file_id = document.file_id
            file_name = document.file_name or f"user_upload_{user.telegram_id}_bottom.jpg"

        # Download the file
        file_bytes = await download_telegram_file(file_id, context.bot)

        # Process and save the image in session
        session.temp_data['custom_bottom_image_data'] = {
            'bytes': file_bytes,
            'name': file_name
        }
        session.temp_data['bottom_icon_id'] = None  # Clear any selected icon
        session.save()

        await update.message.reply_text(
            "Bottom image uploaded successfully."
        )

        # Generate preview
        await generate_preview(update, context)
        return GENERATE_PREVIEW

    except Exception as e:
        await update.message.reply_text(
            f"Error processing image: {str(e)}\n\n"
            "Please try again or select 'Skip'.",
            reply_markup=get_skip_back_keyboard("bottom_icon_upload")
        )
        return UPLOAD_BOTTOM_IMAGE


async def generate_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate invitation preview based on session data"""
    # Get user and session
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Get data from session
    temp_data = session.temp_data

    # Send a "processing" message first
    if update.callback_query:
        message = await update.callback_query.message.reply_text(
            "Generating your invitation preview... ⏳"
        )
    else:
        message = await update.message.reply_text(
            "Generating your invitation preview... ⏳"
        )

    try:
        with transaction.atomic():
            # Create a new invitation object (temporary for preview)
            invitation = Invitation()
            invitation.user = user
            invitation.name = temp_data.get('invitation_name', "Preview")
            invitation.template = Template.objects.get(id=temp_data.get('template_id'))
            invitation.font = Font.objects.get(id=temp_data.get('font_id'))
            invitation.invitation_type = temp_data.get('invitation_type', Invitation.InvitationType.OTHER)
            invitation.text_content = temp_data.get('text_content', "")
            invitation.text_color = temp_data.get('text_color', "#000000")
            invitation.font_size = temp_data.get('font_size', 36)

            # Handle top icon/image
            top_icon_id = temp_data.get('top_icon_id')
            if top_icon_id:
                invitation.top_icon = Icon.objects.get(id=top_icon_id)

            custom_top_image_data = temp_data.get('custom_top_image_data')
            if custom_top_image_data:
                content_file = ContentFile(
                    custom_top_image_data['bytes'],
                    name=custom_top_image_data['name']
                )
                invitation.custom_top_image.save(
                    custom_top_image_data['name'],
                    content_file,
                    save=False
                )

            # Handle bottom icon/image
            bottom_icon_id = temp_data.get('bottom_icon_id')
            if bottom_icon_id:
                invitation.bottom_icon = Icon.objects.get(id=bottom_icon_id)

            custom_bottom_image_data = temp_data.get('custom_bottom_image_data')
            if custom_bottom_image_data:
                content_file = ContentFile(
                    custom_bottom_image_data['bytes'],
                    name=custom_bottom_image_data['name']
                )
                invitation.custom_bottom_image.save(
                    custom_bottom_image_data['name'],
                    content_file,
                    save=False
                )

            # Save invitation to get an ID (but don't commit transaction yet)
            invitation.save()

            # Generate image
            success, error_message = generate_invitation_image(invitation)

            if not success:
                # Rollback transaction if image generation failed
                raise Exception(f"Failed to generate invitation: {error_message}")

            # Store invitation in session
            session.current_invitation = invitation
            session.save()

            # Update processing message and send the preview
            await message.edit_text("Your invitation preview is ready!")

            if invitation.final_image:
                await context.bot.send_photo(
                    chat_id=user_data.id,
                    photo=open(invitation.final_image.path, 'rb'),
                    caption="Here's your invitation preview."
                )

            # Ask if user wants to save the invitation
            await context.bot.send_message(
                chat_id=user_data.id,
                text="Would you like to save this invitation?",
                reply_markup=get_yes_no_keyboard("save_invitation")
            )

            return SAVE_INVITATION

    except Exception as e:
        # Handle any errors
        logger.error(f"Error generating preview: {str(e)}")
        await message.edit_text(
            f"Sorry, there was an error generating your invitation: {str(e)}\n\n"
            "Please try again or make different selections."
        )

        # Return to main menu
        await context.bot.send_message(
            chat_id=user_data.id,
            text="What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU


async def save_invitation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle save invitation response"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    if callback_data == "save_invitation_yes":
        # Invitation was already saved during preview generation
        # We just need to commit the transaction
        invitation = session.current_invitation

        if invitation:
            await query.message.reply_text(
                f"Your invitation '{invitation.name}' has been saved! 🎉\n\n"
                "You can access it anytime from 'My Invitations' in the main menu."
            )
        else:
            await query.message.reply_text(
                "Sorry, there was an error saving your invitation. Please try again."
            )

        # Clear session data
        session.temp_data = {}
        session.current_invitation = None
        session.current_step = 'main_menu'
        session.save()

        # Return to main menu
        await query.message.reply_text(
            "What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    elif callback_data == "save_invitation_no":
        # User doesn't want to save, delete the invitation
        invitation = session.current_invitation
        if invitation:
            invitation.delete()

        # Clear session data
        session.temp_data = {}
        session.current_invitation = None
        session.current_step = 'main_menu'
        session.save()

        # Return to main menu
        await query.message.reply_text(
            "Invitation not saved. What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU


async def view_invitation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle viewing saved invitations"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)

    callback_data = query.data

    # Handle pagination
    if callback_data.startswith("invitation_page_"):
        page = int(callback_data.replace("invitation_page_", ""))
        invitations = Invitation.objects.filter(user=user).order_by('-created_at')
        invitation_list = [(inv.id, inv.name) for inv in invitations]

        await query.edit_message_text(
            "Here are your saved invitations:",
            reply_markup=get_items_keyboard(invitation_list, "invitation", page=page)
        )
        return VIEW_INVITATIONS

    # Handle back button
    if callback_data == "invitation_back":
        await query.message.reply_text(
            "What would you like to do?",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    # Handle invitation selection
    invitation_id = int(callback_data.replace("invitation_", ""))

    try:
        invitation = Invitation.objects.get(id=invitation_id, user=user)

        # Show the invitation
        if invitation.final_image:
            await query.message.reply_photo(
                photo=open(invitation.final_image.path, 'rb'),
                caption=f"Invitation: {invitation.name}"
            )

        # Show actions for this invitation
        keyboard = [
            [InlineKeyboardButton("Send to Someone", callback_data=f"invitation_send_{invitation_id}")],
            [InlineKeyboardButton("Delete", callback_data=f"invitation_delete_{invitation_id}")],
            [InlineKeyboardButton("Back to List", callback_data="invitation_list")]
        ]

        await query.message.reply_text(
            f"What would you like to do with '{invitation.name}'?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return INVITATION_DETAIL

    except Invitation.DoesNotExist:
        await query.message.reply_text(
            "Sorry, that invitation was not found.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU


async def invitation_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle invitation detail actions"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)

    callback_data = query.data

    if callback_data == "invitation_list":
        # Go back to invitation list
        invitations = Invitation.objects.filter(user=user).order_by('-created_at')
        invitation_list = [(inv.id, inv.name) for inv in invitations]

        await query.message.reply_text(
            "Here are your saved invitations:",
            reply_markup=get_items_keyboard(invitation_list, "invitation")
        )
        return VIEW_INVITATIONS

    elif callback_data.startswith("invitation_send_"):
        invitation_id = int(callback_data.replace("invitation_send_", ""))
        invitation = Invitation.objects.get(id=invitation_id, user=user)

        # Send the invitation
        if invitation.final_image:
            await query.message.reply_text(
                "Here's your invitation image. You can forward it to your guests.",
            )

            await query.message.reply_photo(
                photo=open(invitation.final_image.path, 'rb'),
                caption=f"{invitation.name}"
            )

        # Go back to invitation list
        invitations = Invitation.objects.filter(user=user).order_by('-created_at')
        invitation_list = [(inv.id, inv.name) for inv in invitations]

        await query.message.reply_text(
            "Here are your saved invitations:",
            reply_markup=get_items_keyboard(invitation_list, "invitation")
        )
        return VIEW_INVITATIONS

    elif callback_data.startswith("invitation_delete_"):
        invitation_id = int(callback_data.replace("invitation_delete_", ""))
        invitation = Invitation.objects.get(id=invitation_id, user=user)

        # Ask for confirmation before deleting
        keyboard = [
            [
                InlineKeyboardButton("Yes, delete", callback_data=f"confirm_delete_{invitation_id}"),
                InlineKeyboardButton("No, keep it", callback_data="invitation_list")
            ]
        ]

        await query.message.reply_text(
            f"Are you sure you want to delete '{invitation.name}'? This cannot be undone.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return INVITATION_DETAIL

    elif callback_data.startswith("confirm_delete_"):
        invitation_id = int(callback_data.replace("confirm_delete_", ""))
        invitation = Invitation.objects.get(id=invitation_id, user=user)
        invitation_name = invitation.name

        # Delete the invitation
        invitation.delete()

        await query.message.reply_text(
            f"Invitation '{invitation_name}' has been deleted."
        )

        # Check if user has any invitations left
        if Invitation.objects.filter(user=user).exists():
            # Go back to invitation list
            invitations = Invitation.objects.filter(user=user).order_by('-created_at')
            invitation_list = [(inv.id, inv.name) for inv in invitations]

            await query.message.reply_text(
                "Here are your saved invitations:",
                reply_markup=get_items_keyboard(invitation_list, "invitation")
            )
            return VIEW_INVITATIONS
        else:
            # No invitations left, go back to main menu
            await query.message.reply_text(
                "You have no saved invitations. What would you like to do?",
                reply_markup=get_main_menu_keyboard()
            )
            return MAIN_MENU


# Handler for unknown commands or messages
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "Sorry, I didn't understand that command. Please use the provided buttons."
    )
    return ConversationHandler.END


# Default fallback handler
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback handler for conversation"""
    await update.message.reply_text(
        "Sorry, something went wrong. Let's start over.",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENUmessage_text(
        "Please select a template for your invitation:",
        reply_markup=get_items_keyboard(templates, "template", page=page)
    )
    return SELECT_TEMPLATE


# Handle back button
if callback_data == "template_back":
    await query.message.reply_text(
        "Let's create a new invitation! 🎨\n\n"
        "First, what type of invitation are you creating?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(name, callback_data=f"type_{code}")]
            for code, name in get_invitation_types()
        ])
    )
    return CREATE_INVITATION

# Handle template selection
template_id = int(callback_data.replace("template_", ""))
template = Template.objects.get(id=template_id)

# Store template in session
session.temp_data['template_id'] = template_id
session.current_step = 'select_font'
session.save()

# Send template preview
if template.image:
    await query.message.reply_photo(
        photo=open(template.image.path, 'rb'),
        caption=f"Template: {template.name}\n\n{template.description}"
    )

# Show available fonts
fonts = get_fonts()

await query.message.reply_text(
    "Please select a font for your invitation text:",
    reply_markup=get_items_keyboard(fonts, "font")
)
return SELECT_FONT


async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle font selection"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    # Handle pagination
    if callback_data.startswith("font_page_"):
        page = int(callback_data.replace("font_page_", ""))
        fonts = get_fonts()
        await query.edit_message_text(
            "Please select a font for your invitation text:",
            reply_markup=get_items_keyboard(fonts, "font", page=page)
        )
        return SELECT_FONT

    # Handle back button
    if callback_data == "font_back":
        templates = get_active_templates()
        await query.message.reply_text(
            "Please select a template for your invitation:",
            reply_markup=get_items_keyboard(templates, "template")
        )
        return SELECT_TEMPLATE

    # Handle font selection
    font_id = int(callback_data.replace("font_", ""))
    font = Font.objects.get(id=font_id)

    # Store font in session
    session.temp_data['font_id'] = font_id
    session.current_step = 'enter_text'
    session.save()

    # Send font preview if available
    if font.preview:
        await query.message.reply_photo(
            photo=open(font.preview.path, 'rb'),
            caption=f"Font: {font.name}"
        )

    # Ask for invitation text
    await query.message.reply_text(
        "Now, please enter the text for your invitation. You can use multiple lines.\n\n"
        "Example:\n"
        "You are cordially invited to\n"
        "Sarah & John's Wedding\n"
        "June 15, 2025 at 3:00 PM\n"
        "Grand Plaza Hotel, New York\n"
        "RSVP by May 15"
    )
    return ENTER_TEXT


async def process_invitation_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the invitation text entered by the user"""
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Get the invitation text from the message
    invitation_text = update.message.text

    # Store the invitation text in the session
    session.temp_data['text_content'] = invitation_text
    session.current_step = 'choose_text_color'
    session.save()

    # Ask for text color
    await update.message.reply_text(
        "Please select a color for your text:",
        reply_markup=get_color_keyboard()
    )
    return CHOOSE_TEXT_COLOR


async def color_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text color selection"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    # Handle back button
    if callback_data == "color_back":
        await query.message.reply_text(
            "Please enter the text for your invitation again:"
        )
        return ENTER_TEXT

    # Handle color selection
    color_code = callback_data.replace("color_", "")

    # Store color in session
    session.temp_data['text_color'] = color_code
    session.current_step = 'select_top_icon'
    session.save()

    # Ask if user wants to add a top icon
    await query.message.reply_text(
        "Would you like to add an icon at the top of your invitation?",
        reply_markup=get_yes_no_keyboard("top_icon")
    )
    return SELECT_TOP_ICON


async def top_icon_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle top icon selection"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    if callback_data == "top_icon_yes":
        # Show icon options and custom upload
        options_keyboard = [
            [InlineKeyboardButton("Select from library", callback_data="top_icon_library")],
            [InlineKeyboardButton("Upload my own", callback_data="top_icon_upload")],
            [InlineKeyboardButton("Back", callback_data="top_icon_back")]
        ]

        await query.edit_message_text(
            "How would you like to add a top icon?",
            reply_markup=InlineKeyboardMarkup(options_keyboard)
        )
        return SELECT_TOP_ICON

    elif callback_data == "top_icon_library":
        # Show available icons
        icons = get_icons()

        await query.message.reply_text(
            "Please select an icon:",
            reply_markup=get_items_keyboard(icons, "top_icon_select")
        )
        return SELECT_TOP_ICON

    elif callback_data == "top_icon_select_back":
        # Go back to icon options
        options_keyboard = [
            [InlineKeyboardButton("Select from library", callback_data="top_icon_library")],
            [InlineKeyboardButton("Upload my own", callback_data="top_icon_upload")],
            [InlineKeyboardButton("Back", callback_data="top_icon_back")]
        ]

        await query.edit_message_text(
            "How would you like to add a top icon?",
            reply_markup=InlineKeyboardMarkup(options_keyboard)
        )
        return SELECT_TOP_ICON

    elif callback_data.startswith("top_icon_select_page_"):
        # Handle pagination for icons
        page = int(callback_data.replace("top_icon_select_page_", ""))
        icons = get_icons()

        await query.edit_message_text(
            "Please select an icon:",
            reply_markup=get_items_keyboard(icons, "top_icon_select", page=page)
        )
        return SELECT_TOP_ICON

    elif callback_data.startswith("top_icon_select_"):
        # Handle icon selection
        icon_id = int(callback_data.replace("top_icon_select_", ""))

        # Store icon in session
        session.temp_data['top_icon_id'] = icon_id
        session.save()

        # Show selected icon
        icon = Icon.objects.get(id=icon_id)
        await query.message.reply_photo(
            photo=open(icon.image.path, 'rb'),
            caption=f"Selected top icon: {icon.name}"
        )

        # Move to bottom icon selection
        await query.message.reply_text(
            "Would you like to add an icon at the bottom of your invitation?",
            reply_markup=get_yes_no_keyboard("bottom_icon")
        )
        return SELECT_BOTTOM_ICON

    elif callback_data == "top_icon_upload":
        # Prompt user to upload image
        await query.message.reply_text(
            "Please upload an image to use as the top icon.\n\n"
            "For best results, use a PNG image with transparency, ideally less than 500x500 pixels."
        )
        return UPLOAD_TOP_IMAGE

    elif callback_data == "top_icon_back":
        # Go back to text color selection
        await query.message.reply_text(
            "Please select a color for your text:",
            reply_markup=get_color_keyboard()
        )
        return CHOOSE_TEXT_COLOR

    elif callback_data == "top_icon_no":
        # Skip top icon, move to bottom icon
        session.temp_data['top_icon_id'] = None
        session.temp_data['custom_top_image'] = None
        session.save()

        # Ask if user wants to add a bottom icon
        await query.message.reply_text(
            "Would you like to add an icon at the bottom of your invitation?",
            reply_markup=get_yes_no_keyboard("bottom_icon")
        )
        return SELECT_BOTTOM_ICON

    return SELECT_TOP_ICON


async def process_top_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process uploaded top image"""
    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    # Check if a photo was uploaded
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "Please upload an image file.",
            reply_markup=get_skip_back_keyboard("top_icon_upload")
        )
        return UPLOAD_TOP_IMAGE

    try:
        if update.message.photo:
            # Get the largest photo size
            file_id = update.message.photo[-1].file_id
            file_name = f"user_upload_{user.telegram_id}_top.jpg"
        else:
            # Handle document upload
            document = update.message.document
            if not document.mime_type.startswith('image/'):
                raise Exception("Please upload an image file.")

            file_id = document.file_id
            file_name = document.file_name or f"user_upload_{user.telegram_id}_top.jpg"

        # Download the file
        file_bytes = await download_telegram_file(file_id, context.bot)

        # Process and save the image in session
        session.temp_data['custom_top_image_data'] = {
            'bytes': file_bytes,
            'name': file_name
        }
        session.temp_data['top_icon_id'] = None  # Clear any selected icon
        session.save()

        await update.message.reply_text(
            "Top image uploaded successfully.",
        )

        # Move to bottom icon selection
        await update.message.reply_text(
            "Would you like to add an icon at the bottom of your invitation?",
            reply_markup=get_yes_no_keyboard("bottom_icon")
        )
        return SELECT_BOTTOM_ICON

    except Exception as e:
        await update.message.reply_text(
            f"Error processing image: {str(e)}\n\n"
            "Please try again or select 'Skip'.",
            reply_markup=get_skip_back_keyboard("top_icon_upload")
        )
        return UPLOAD_TOP_IMAGE


# Similar handlers for bottom icon selection and image upload
async def bottom_icon_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bottom icon selection - similar to top_icon_callback"""
    query = update.callback_query
    await query.answer()

    user_data = update.effective_user
    user = get_or_create_user(user_data)
    session = get_or_create_session(user)

    callback_data = query.data

    if callback_data == "bottom_icon_yes":
        # Show icon options and custom upload
        options_keyboard = [
            [InlineKeyboardButton("Select from library", callback_data="bottom_icon_library")],
            [InlineKeyboardButton("Upload my own", callback_data="bottom_icon_upload")],
            [InlineKeyboardButton("Back", callback_data="bottom_icon_back")]
        ]

        await query.edit_