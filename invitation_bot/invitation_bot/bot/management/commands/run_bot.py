from django.core.management.base import BaseCommand
from invitation_bot.bot.telegram_bot import run_bot
# from bot.telegram_bot import run_bot

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting the Telegram bot...'))
        run_bot()