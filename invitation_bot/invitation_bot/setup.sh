#!/bin/bash

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "SECRET_KEY=your-secret-key-here" > .env
    echo "DEBUG=True" >> .env
    echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
    echo "TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here" >> .env
    echo "Please edit the .env file with your Telegram bot token."
fi

# Set up database
echo "Setting up database..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Create media directories
echo "Creating media directories..."
mkdir -p media/templates
mkdir -p media/fonts
mkdir -p media/icons
mkdir -p media/uploads
mkdir -p media/invitations

echo "Setup complete!"
echo "To run the Django admin, use: python manage.py runserver"
echo "To run the Telegram bot, use: python manage.py run_bot"