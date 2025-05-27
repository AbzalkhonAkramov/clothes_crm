from decimal import Decimal

import openai
import requests
import tiktoken

from root import settings
from root.settings import TIME_PRICES, TELEGRAM_BOT_TOKEN

openai.api_key = settings.OPENAI_API_KEY


def count_tokens(text, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        num_tokens = len(tokens)

        return num_tokens
    except ValueError as e:
        raise ValueError(f"Unknown model: {model}. Error: {e}")


def send_telegram_message(chat_id, text):
    data = {
        'chat_id': chat_id,
        'text': text,
    }

    response = requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', data=data)
    print("send telegram message status", response.json())


def send_request_openai(prompt_system, prompt_user, model: str = "gpt-4o", user=None):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': prompt_user},
            ]
        )
        print(completion)
        output = completion.choices[0].message.content.strip()

        input_tokens = count_tokens(prompt_user)
        output_tokens = count_tokens(output)

        if input_tokens and output_tokens and user:
            input_price = Decimal(input_tokens) * Decimal('0.189')
            output_price = Decimal(output_tokens) * Decimal('0.57')
            total_price = input_price + output_price
            user.credit_seconds -= total_price / TIME_PRICES.get('second')
            user.used_seconds += total_price / TIME_PRICES.get('second')
            user.credit_sums -= total_price
            user.used_sums += total_price
            user.save()

        return output
    except openai.OpenAIError as e:
        send_telegram_message('715352534', str(e))
        raise e


def transcribe_audio_whisper(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, language="en")
        return True, transcript['text']
    except openai.AuthenticationError:
        return False, f"Authentication failed. Please check your API key."
    except openai.RateLimitError as e:
        return False, f"Rate limit exceeded. Please wait and try again later.{str(e)}"
    except openai.APIConnectionError:
        return False, f"Connection error occurred. Please check your internet connection."
    except openai.OpenAIError as e:
        return False, f"An error occurred with the OpenAI service: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"
