import asyncio
import json
import logging
import os
from re import sub as re_sub
from uuid import UUID

import requests
import tiktoken
import yaml
from django.db import transaction
from requests import post
from rest_framework.exceptions import ValidationError

from root.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN
from users.models import Translate, Project, Article, Summary
from users.models.related import SpeechtotextForBot
from users.utils.openai_utils2 import send_request_openai
from users.utils.promt_data import uz_ru_prompt, uz_en_prompt, ru_uz_prompt, ru_en_prompt, en_ru_prompt, en_uz_prompt, \
    auto_en_prompt, auto_uz_prompt, auto_ru_prompt, article_prompt, interview_prompt, news_prompt, reportage_prompt, \
    summary_prompt
from users.utils.speech_to_text import write_to_docx, write_to_docx2

logger = logging.getLogger(__name__)


def send_message(chat_id, text, reply_markup=None):
    logging.debug(f'data {chat_id}, {text}, {reply_markup}')
    r = post(f'{TELEGRAM_URL}/sendMessage',
             params={'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup})
    logging.debug(f'telegram bot: {r.url}')
    logging.debug(f'telegram bot: {r.json()}')
    if r.status_code == 200:
        return r.json()


def convert_credits_to_time(credits, lang):
    hours = int(credits // 3600)
    minutes = int((credits % 3600) // 60)
    seconds = int(credits % 60)

    translations = {
        'uz': {'hours': 'soat', 'minutes': 'daqiqa', 'seconds': 'soniya'},
        'en': {'hours': 'hours', 'minutes': 'minutes', 'seconds': 'seconds'},
        'ru': {'hours': 'часов', 'minutes': 'минут', 'seconds': 'секунд'}
    }

    lang_translations = translations.get(lang, translations['en'])
    time_parts = []
    if hours:
        time_parts.append(f"{hours} {lang_translations['hours']}")
    if minutes:
        time_parts.append(f"{minutes} {lang_translations['minutes']}")
    if seconds or not time_parts:
        time_parts.append(f"{seconds} {lang_translations['seconds']}")

    formatted_time = " ".join(time_parts)
    return formatted_time


def generate_slug(text: str) -> str:
    text = text[:20]
    s = re_sub(r'[^\w\s-]', '', text).strip().lower()
    s = re_sub(r'\s+', '_', s)
    s = re_sub(r'-+', '_', s)
    return s


def send_telegram_message(chat_id, text):
    data = {
        'chat_id': chat_id,
        'text': text,
    }

    response = requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', data=data)
    print("send telegram message status", response.json())


def human_bytes(size):
    if not size:
        return ""

    power = 1024
    n = 0
    units = ('B', 'KB', 'MB', 'GB', 'TB')

    while size >= power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{round(size, 2)} {units[n]}"


def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


def load_yaml(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


loaded_yaml = load_yaml("tranlations.yml")


def lang_result(translation_choice):
    prompts = {
        'uz-ru': uz_ru_prompt,
        'uz-en': uz_en_prompt,
        'ru-uz': ru_uz_prompt,
        'ru-en': ru_en_prompt,
        'en-ru': en_ru_prompt,
        'en-uz': en_uz_prompt,
        'auto-en': auto_en_prompt,
        'auto-uz': auto_uz_prompt,
        'auto-ru': auto_ru_prompt,
    }
    return prompts.get(translation_choice, "Noma'lum tarjima varianti")


def send_telegram_docx(user_id, file_path, file_name, lang):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"Summary", "callback_data": f"summarylang-{file_name}-{lang}"}
            ],
            [
                {"text": f"Translate", "callback_data": f"translation-{file_name}-{lang}"}
            ],
            [
                {"text": f"Article", "callback_data": f"makearticlelang-{file_name}"}
            ],

        ]
    }

    data = {
        'chat_id': user_id,
        'caption': '#document',
        'reply_markup': json.dumps(keyboard)
    }
    print(data)
    with open(file_path, 'rb') as doc:
        r = requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                          data=data,
                          files={'document': (
                              file_path, doc,
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        print("send telegram status", r.json())


def send_telegram_docx_no_keyboard(user_id, file_path):
    data = {
        'chat_id': user_id,
        'caption': '#document',
    }

    print(data)
    with open(file_path, 'rb') as doc:
        r = requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                          data=data,
                          files={'document': (
                              file_path, doc,
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        print("send telegram status", r.json())


@transaction.atomic
def process_summary_article_translate_action(project, user, result_text):
    if project.action_type == Project.ActionChoices.SUMMARY:
        model = "gpt-4o"
        if not isinstance(result_text, str):
            raise ValueError("result_text should be a string")
        if not isinstance(summary_prompt, str):
            raise ValueError("summary_prompt should be a string")

        result_answer = send_request_openai(summary_prompt, result_text, model, user)
        logger.info(f"Prompt: {summary_prompt}++++++++++++++++++++++++++++++++++++++++++")
        logger.info(f"User: {user}")
        logger.info(f"Project: {project}")

        tr_lang_prompt = lang_result(f"auto-{project.lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)

        output_docx = write_to_docx(result_answer, project.id, f"{project.name}_summary")
        summary = Summary.objects.create(user=user, project=project, lang=project.lang, output_text=result_answer,
                                         output_docx=output_docx)
        return summary


    elif project.action_type == Project.ActionChoices.ARTICLE:
        if project.article_type == "article":
            prompt = article_prompt
        elif project.article_type == "interview":
            prompt = interview_prompt
        elif project.article_type == "news":
            prompt = news_prompt
        elif project.article_type == "reportage":
            prompt = reportage_prompt
        else:
            raise ValidationError('Invalid article type', code="invalid_article_type", )

        result_answer = send_request_openai(prompt, result_text, "gpt-4o", user)

        tr_lang_prompt = lang_result(f"auto-{project.lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)

        output_docx = write_to_docx(result_answer, project.id, f"{project.name}_article")
        article = Article.objects.create(user=user, project=project, lang=project.lang, type=project.article_type,
                                         output_text=result_answer,
                                         output_docx=output_docx)
        return article

    elif project.action_type == Project.ActionChoices.TRANSLATE:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(result_text)
        translated_texts = []

        max_tokens = 127000
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = encoding.decode(chunk_tokens)
            tr_lang_prompt = lang_result(f"auto-{project.lang[:2]}")
            translated_chunk = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=chunk_text, model="gpt-4o",
                                                   user=user)
            translated_texts.append(translated_chunk)

        translated_text = ''.join(translated_texts)
        output_docx = write_to_docx(translated_text, project.id, f"{project.name}_translate")
        translate = Translate.objects.create(user=user, project=project, lang=project.lang, output_text=translated_text,
                                             output_docx=output_docx)
        return translate


@transaction.atomic
def process_summary_article_translate_action_for_bot(stt, user, result_text):
    if stt.type == SpeechtotextForBot.SpeechtotextForBotChoices.SUMMARY:
        model = "gpt-4o"
        if not isinstance(result_text, str):
            raise ValueError("result_text should be a string")
        if not isinstance(summary_prompt, str):
            raise ValueError("summary_prompt should be a string")

        result_answer = send_request_openai(summary_prompt, result_text, model, user)
        logger.info(f"Prompt: {summary_prompt}++++++++++++++++++++++++++++++++++++++++++")
        logger.info(f"User: {user}")
        logger.info(f"STT: {stt}")

        tr_lang_prompt = lang_result(f"auto-{stt.lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)
        file_path, file_name = write_to_docx2(result_answer, stt.id, f"{result_answer[:20]}_summary")

        return file_path, file_name


    elif stt.type in ('article', 'interview', 'news', 'reportage'):
        if stt.type == "article":
            prompt = article_prompt
        elif stt.type == "interview":
            prompt = interview_prompt
        elif stt.type == "news":
            prompt = news_prompt
        elif stt.type == "reportage":
            prompt = reportage_prompt
        else:
            raise ValidationError('Invalid article type', code="invalid_article_type", )

        result_answer = send_request_openai(prompt, result_text, "gpt-4o", user)

        tr_lang_prompt = lang_result(f"auto-{stt.lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)

        file_path, file_name = write_to_docx2(result_answer, stt.id, f"{result_answer[:20]}_article")

        return file_path, file_name
