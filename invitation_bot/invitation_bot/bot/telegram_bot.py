import os
import logging
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invitation_bot.settings')
django.setup()

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)

from .bot_handlers import (
    start, help_command, main_menu, unknown, fallback,
    invitation_type_callback, process_invitation_name, template_callback,
    font_callback, process_invitation_text, color_callback,
    top_icon_callback, process_top_image_upload,
    bottom_icon_callback, process_bottom_image_upload,
    save_invitation_callback, view_invitation_callback, invitation_detail_callback,
    START, MAIN_MENU, CREATE_INVITATION, SELECT_TEMPLATE, SELECT_FONT,
    ENTER_TEXT, CHOOSE_TEXT_COLOR, SELECT_TOP_ICON, UPLOAD_TOP_IMAGE,
    SELECT_BOTTOM_ICON, UPLOAD_BOTTOM_IMAGE, GENERATE_PREVIEW,
    SAVE_INVITATION, VIEW_INVITATIONS, INVITATION_DETAIL, HELP
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def setup_bot():
    """Set up the Telegram bot"""
    # Get bot token from settings
    token = settings.TELEGRAM_BOT_TOKEN

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in settings")
        return None

    # Create the application
    application = ApplicationBuilder().token(token).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [CommandHandler('start', start)],

            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
                CommandHandler('help', help_command)
            ],

            CREATE_INVITATION: [
                CallbackQueryHandler(invitation_type_callback, pattern=r'^type_')
            ],

            SELECT_TEMPLATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_invitation_name),
                CallbackQueryHandler(template_callback, pattern=r'^template_')
            ],

            SELECT_FONT: [
                CallbackQueryHandler(font_callback, pattern=r'^font_')
            ],

            ENTER_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_invitation_text)
            ],

            CHOOSE_TEXT_COLOR: [
                CallbackQueryHandler(color_callback, pattern=r'^color_')
            ],

            SELECT_TOP_ICON: [
                CallbackQueryHandler(top_icon_callback, pattern=r'^top_icon_')
            ],

            UPLOAD_TOP_IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, process_top_image_upload),
                CallbackQueryHandler(top_icon_callback, pattern=r'^top_icon_')
            ],

            SELECT_BOTTOM_ICON: [
                CallbackQueryHandler(bottom_icon_callback, pattern=r'^bottom_icon_')
            ],

            UPLOAD_BOTTOM_IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, process_bottom_image_upload),
                CallbackQueryHandler(bottom_icon_callback, pattern=r'^bottom_icon_')
            ],

            GENERATE_PREVIEW: [],  # Just a transition state

            SAVE_INVITATION: [
                CallbackQueryHandler(save_invitation_callback, pattern=r'^save_invitation_')
            ],

            VIEW_INVITATIONS: [
                CallbackQueryHandler(view_invitation_callback, pattern=r'^invitation_')
            ],

            INVITATION_DETAIL: [
                CallbackQueryHandler(invitation_detail_callback)
            ],

            HELP: [
                CommandHandler('help', help_command)
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(filters.ALL, fallback)
        ]
    )

    # Add handlers
    application.add_handler(conv_handler)

    # Add a handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    return application


def run_bot():
    """Run the Telegram bot"""
    application = setup_bot()

    if application:
        logger.info("Starting bot...")
        application.run_polling()
    else:
        logger.error("Failed to set up bot")


if __name__ == "__main__":
    run_bot()