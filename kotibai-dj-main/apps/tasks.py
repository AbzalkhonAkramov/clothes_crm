import json
import os
import subprocess
from decimal import Decimal

import requests
from celery import shared_task
from celery.bin.control import status
from docx import Document
from loguru import logger
from pydub import AudioSegment
from rest_framework.exceptions import ValidationError

from payments.utils import payment_status_approval
from root.settings import TIME_PRICES, TELEGRAM_BOT_TOKEN, MEDIA_ROOT
from users.models import Speechtotext, User, Summary, Article
from users.models.related import SpeechtotextForBot, Translate, Project
from users.utils import generate_slug, send_telegram_message, send_telegram_docx, \
    process_summary_article_translate_action, process_summary_article_translate_action_for_bot, \
    send_telegram_docx_no_keyboard, loaded_yaml, send_request_openai, lang_result
from users.utils.eleven_labs import speech_to_text_eleven_labs
from users.utils.openai_utils2 import transcribe_audio_whisper
from users.utils.promt_data import transcript_edit_prompt_uz, transcript_edit_prompt_ru, summary_prompt, article_prompt, \
    news_prompt, reportage_prompt, interview_prompt, transcript_edit_prompt_en
from users.utils.send_notification import send_firebase_notification
from users.utils.speech_to_text import convert_to_wav_v2, write_to_docx2, write_to_docx
from users.utils.transcript_edit import transcript_edit_openai


@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_seconds=30)
def payment_status_check(self, transaction_id, payment_id=None, current_date=None):
    try:
        result = payment_status_approval(transaction_id, payment_id, current_date)
        if not result[0]:
            raise Exception("Payment status check failed - triggering retry")
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f'Max retries exceeded for task {self.request.id} with transaction_id {transaction_id}')
            return False
        except Exception as exc:
            logger.error(f'{exc} for task {self.request.id}')


def get_audio_duration(input_file):
    result = subprocess.run(['ffmpeg', '-i', input_file], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = result.stderr.decode()
    for line in output.split('\n'):
        if 'Duration' in line:
            duration_str = line.split('Duration: ')[1].split(',')[0]
            hours, minutes, seconds = duration_str.split(':')
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            return int(total_seconds)
    return None


@shared_task()
def process_speech_to_text(speech_to_text_id, input_file=None, lang=None, token=None):
    speech_to_text = Speechtotext.objects.get(id=speech_to_text_id)
    try:
        user = speech_to_text.user
        user_id = user.telegram_id

        if input_file:
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"No such file or directory: '{input_file}'")
        else:
            speech_to_text.delete()
            raise ValidationError("Please provide an input_file or youtube_link")

        duration = get_audio_duration(input_file)
        if not duration:
            duration = 100
            send_telegram_message("715352534", "Audio duration not found. to'g'rilab qo'y tezda. task.py line 75")
        if duration > user.credit_seconds:
            send_telegram_message(user_id,
                                  "Sizning hissobingiz yetarli emas! \nSizning so'rovingiz bekor qilindi.\nHissobingizni yetarli mablag'ga to'ldiring va qayta so'rov yuboring")
            speech_to_text.delete()
            return

        if lang == 'uz-UZ':
            result = speech_to_text_eleven_labs(input_file, language_code='uzb')
            result_text = result.text
            result_text = transcript_edit_openai(transcript_edit_prompt_uz, result_text)
        elif lang == 'ru-RU':
            result = speech_to_text_eleven_labs(input_file, language_code='rus')
            result_text = result.text
            result_text = transcript_edit_openai(transcript_edit_prompt_ru, result_text)
        elif lang == 'en-US':
            result = speech_to_text_eleven_labs(input_file, language_code='eng')
            result_text = result.text
            result_text = transcript_edit_openai(transcript_edit_prompt_en, result_text)
        else:
            print(lang, "++++++++++++++++++++++")
        print(lang, "++++++++++++++++++++++")

        file_name = f"kotibaibot_{speech_to_text_id}.docx"
        doc = Document()
        doc.add_paragraph(result_text)
        file_path = os.path.join(MEDIA_ROOT, file_name)
        doc.save(file_path)
        print(f"Saved {file_path}")
        speech_to_text.output_text = result_text
        speech_to_text.output_docx = file_name
        speech_to_text.file_name = file_name
        speech_to_text.save()
        # text = loaded_yaml['transcripted'].get(user_lang)

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
            duration = Decimal(duration)
        user.credit_seconds -= duration
        user.used_seconds += duration
        user.credit_sums -= duration * TIME_PRICES.get('second')
        user.used_sums += duration * TIME_PRICES.get('second')
        user.save()
        project = speech_to_text.project
        project.loading = False
        project.save()
        if token:
            send_firebase_notification(token, f"dashboard.kotib.ai",
                                       "Sizning transkripsiyangiz yakunlandi", project.id)

        return f"{True}, TUGADI😁😁😁😁"
    except Exception as e:
        project = speech_to_text.project
        project.delete()
        raise e


@shared_task()
def uzbek_voice(voice_id, text):
    result_answer = text
    stt = Speechtotext.objects.filter(voice_id=voice_id).first()

    if stt:
        if len(text) > 100:
            try:
                lang = stt.lang
                if lang == 'ru-RU':
                    prompt = transcript_edit_prompt_ru
                else:
                    prompt = transcript_edit_prompt_uz

                result_answer = transcript_edit_openai(prompt, text, user=stt.user)
            except Exception as e:
                logger.error(str(e))
        file_path, file_name = write_to_docx2(result_answer, stt.project.id, f"{stt.project.name}_transcript")
        stt.output_docx = file_name
        stt.file_name = file_name
        stt.output_text = result_answer
        stt.save()
        user = stt.user
        duration = stt.file_duration
        user.credit_seconds -= duration
        user.used_seconds += duration
        user.credit_sums -= duration * TIME_PRICES.get('second')
        user.used_sums += duration * TIME_PRICES.get('second')
        user.save()
        send_telegram_docx(user.telegram_id, file_path, stt.file_name, user.lang)
        if user.device_token:
            send_firebase_notification(user.device_token, f"dashboard.kotib.ai", "Tayyor bo'ldi", stt.id)
        project = stt.project
        project.loading = False
        project.save()
        return {
            "id": stt.id,
            "file_name": stt.file_name,
            "user": stt.user.first_name,
            "project": stt.project.id,
        }
    else:
        sttforbot = SpeechtotextForBot.objects.filter(voice_id=voice_id).first()
        if sttforbot:
            user = sttforbot.user
            if sttforbot.type != SpeechtotextForBot.SpeechtotextForBotChoices.STT:
                file_path, file_name = process_summary_article_translate_action_for_bot(sttforbot, user, text)
                send_telegram_docx_no_keyboard(user.telegram_id, file_path)
            else:
                if len(text) > 100:
                    try:
                        lang = sttforbot.lang
                        if lang == 'ru-RU':
                            prompt = transcript_edit_prompt_ru
                        else:
                            prompt = transcript_edit_prompt_uz

                        result_answer = transcript_edit_openai(prompt, text, user=sttforbot.user)
                        file_path, file_name = write_to_docx2(result_answer, sttforbot.id, user.telegram_id)
                        send_telegram_docx(user.telegram_id, file_path, file_name, user.lang)
                        print(status, "+++++++++++++++++++++++++")
                    except Exception as e:
                        logger.error(str(e))
                else:
                    file_path, file_name = write_to_docx2(result_answer, sttforbot.id, user.telegram_id)
                    send_telegram_docx(user.telegram_id, file_path, file_name, user.lang)
            duration = sttforbot.duration
            user.credit_seconds -= duration
            user.used_seconds += duration
            user.credit_sums -= duration * TIME_PRICES.get('second')
            user.used_sums += duration * TIME_PRICES.get('second')
            user.save()

            if user.device_token:
                send_firebase_notification(user.device_token, f"dashboard.kotib.ai", "Tayyor bo'ldi", sttforbot.id)

            return {
                "id": sttforbot.id,
                "user": sttforbot.user.first_name,

            }
        else:
            return None


@shared_task()
def uzbek_voice_for_other(voice_id, text):
    stt = Speechtotext.objects.filter(voice_id=voice_id).first()
    if stt:
        file_path, file_name = write_to_docx2(text, stt.project.id, stt.project.name)
        stt.output_docx = file_name
        stt.file_name = file_name
        stt.output_text = text
        stt.save()
        user = stt.user
        duration = stt.file_duration
        user.credit_seconds -= duration
        user.used_seconds += duration
        user.credit_sums -= duration * TIME_PRICES.get('second')
        user.used_sums += duration * TIME_PRICES.get('second')
        user.save()
        project = stt.project
        process_summary_article_translate_action(project, user, text)
        if user.device_token:
            send_firebase_notification(user.device_token, f"dashboard.kotib.ai", "Tayyor bo'ldi", project.id)
        project.loading = False
        project.save()
        return {
            "id": stt.id,
            "file_name": stt.file_name,
            "user": stt.user.first_name,
            "project": stt.project.id,
        }
    else:
        return None


@shared_task()
def translate_tasks(project_id, user_id, text, lang, prompt):
    project = Project.objects.get(id=project_id)
    user = User.objects.get(id=user_id)
    translated_text = transcript_edit_openai(prompt, text, user=user)
    output_docx = write_to_docx(translated_text, project.id, f"{project.name}_translate")
    translate = Translate.objects.create(user=user, project=project, lang=lang, output_text=translated_text,
                                         output_docx=output_docx)
    project.loading = False
    project.save()

    if user.device_token:
        send_firebase_notification(user.device_token, f"dashboard.kotib.ai", "Tayyor bo'ldi", project.id)

    return {
        "id": translate.id,
        "user": translate.user.id,
        "project": project.id,
    }


@shared_task()
def process_summary_article(project_id, user_id, audio_filename, duration):
    user = User.objects.get(id=user_id)
    project = Project.objects.get(id=project_id)
    try:
        result = speech_to_text_eleven_labs(audio_filename)
    except Exception as e:
        send_telegram_message("715352534", str(e))
        raise e
    result_text = result.text
    type = Project.ActionChoices.SUMMARY
    if type == Project.ActionChoices.ARTICLE:
        type = project.article_type
    if type == 'summary':
        prompt = summary_prompt
    elif type == 'article':
        prompt = article_prompt
    elif type == 'news':
        prompt = news_prompt
    elif type == 'reportage':
        prompt = reportage_prompt
    else:
        prompt = interview_prompt

    result_text = send_request_openai(prompt, result_text, "gpt-4o", user=user)
    tr_lang_prompt = lang_result(f"auto-{project.lang.split('-')[0]}")
    result_text = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_text, model="gpt-4o", user=user)
    file_path, file_name = write_to_docx2(result_text, project.id, project.name)
    send_telegram_docx_no_keyboard(user.telegram_id, file_path)
    if project.action_type == 'summary':
        summary = Summary.objects.create(user=user, project=project, lang=project.lang, output_docx=file_name,
                                         output_text=result_text)
    else:
        article = Article.objects.create(user=user, project=project, lang=project.lang, type=type, output_docx=file_name,
                                         output_text=result_text)
    duration = Decimal(duration)
    user.credit_seconds -= duration
    user.used_seconds += duration
    user.credit_sums -= duration * TIME_PRICES.get('second')
    user.used_sums += duration * TIME_PRICES.get('second')
    user.save()
    project.loading = False
    project.save()
    if user.device_token:
        send_firebase_notification(user.device_token, f"dashboard.kotib.ai", "Tayyor bo'ldi", project.id)
    return {
        "id": project.id,
        "result_text": result_text,
        "user": project.user.first_name
    }
