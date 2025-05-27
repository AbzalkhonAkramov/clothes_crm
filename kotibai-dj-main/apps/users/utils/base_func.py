import os

from django.core.files import File
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from rest_framework.exceptions import ValidationError
from loguru import logger
from users.models import Project, Summary, Article, Speechtotext
from users.utils.parser import scrape_site
from users.utils.speech_to_text import read_docx, write_to_docx, convert_to_wav_v2
from users.utils.openai_utils2 import send_request_openai
from users.utils.promt_data import summary_prompt, article_prompt, interview_prompt, news_prompt, reportage_prompt
from users.utils import lang_result
from users.utils.uzbekvoice import stt_api
from users.utils.youtube_audio_downloader import download_audio_from_youtube
from tasks import process_speech_to_text, translate_tasks, process_summary_article, get_audio_duration


def process_project_action(project, user, lang, article_type, input_type):
    stt_obj = getattr(project, 'stt', None)
    if input_type == 'site_link':
        result_text = scrape_site(project.input_text)
    elif input_type == 'docx':
        result_text = read_docx(project.input_file)
    else:
        if stt_obj and project.stt.output_docx:
            result_text = read_docx(project.stt.output_docx.path)
        elif project.input_text:
            result_text = project.input_text
        elif project.input_file:
            result_text = read_docx(project.input_file.path)
        else:
            raise ValidationError("Project Input text or input file is empty.", code="project_input_empty")
    if project.action_type == Project.ActionChoices.SUMMARY:
        model = "gpt-4o"
        result_answer = send_request_openai(summary_prompt, result_text, model, user)

        tr_lang_prompt = lang_result(f"auto-{lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)
        output_docx = write_to_docx(result_answer, project.id, f"{project.name}_summary")
        Summary.objects.create(user=user, project=project, lang=lang, output_text=result_answer,
                               output_docx=output_docx)


    elif project.action_type == Project.ActionChoices.ARTICLE:
        if article_type == "article":
            prompt = article_prompt
        elif article_type == "interview":
            prompt = interview_prompt
        elif article_type == "news":
            prompt = news_prompt
        elif article_type == "reportage":
            prompt = reportage_prompt
        else:
            raise ValidationError('Invalid article type', code="invalid_article_type", )

        result_answer = send_request_openai(prompt, result_text, "gpt-4o", user)

        tr_lang_prompt = lang_result(f"auto-{lang[:2]}")
        result_answer = send_request_openai(prompt_system=tr_lang_prompt, prompt_user=result_answer, model="gpt-4o",
                                            user=user)

        output_docx = write_to_docx(result_answer, project.id, f"{project.name}_article")
        Article.objects.create(user=user, project=project, lang=lang, output_text=result_answer,
                               output_docx=output_docx)

    elif project.action_type == Project.ActionChoices.TRANSLATE:
        tr_lang_prompt = lang_result(f"auto-{lang[:2]}")
        tasks = translate_tasks.delay(project.id, user.id, result_text, lang, tr_lang_prompt)
        project.loading = True
        project.save()


def delete_project_with_files(project):
    """
    Custom method to delete a project and associated files.
    """
    try:
        if project.input_file:
            project.input_file.delete(save=False)  # Delete associated file if any
        project.delete()  # Delete the project instance itself
    except Exception as e:
        logger.error(f"Failed to delete project {project.id}: {str(e)}")


def stt_create_and_process(project, user, lang):
    try:
        youtube_link = project.input_text
        speechtotext = None
        if youtube_link:
            youtube_file = download_audio_from_youtube(youtube_link)
            if youtube_file:
                with open(youtube_file, 'rb') as f:
                    project.input_file.save(f"{project.id}_audio.mp3", File(f))
                project.save()
                file_path = project.input_file.path
                if os.path.exists(youtube_file):
                    os.remove(youtube_file)
            else:
                raise ValidationError("Could not download audio from YouTube.", code="youtube_link")
        else:
            file_path = project.input_file.path
            logger.debug(
                f'Attempting to open file: {file_path}+++++++++++++++++++++++++++++\n++++++++++++++++++++++\n++++++++++++++++++++++++++')
        file_size = os.path.getsize(file_path)

        if file_size > 1024 * 1024 * 1024:  # 1 GB
            raise ValidationError("File size must be max 1 gb", code="incorrect_size")
        if not file_path.endswith(('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')):
            if file_path.endswith(('.flac', '.aac', '.ogg', '.avi', '.mov', '.wmv',
                                   '.mkv', '.flv', '.3gp')):
                file_path = convert_to_wav_v2(file_path)
            else:
                raise ValidationError("Incorrect file format. choose one: audio or video", code="incorrect_format")
        speechtotext = Speechtotext.objects.create(user=user, project=project, lang=lang)
        project.loading = True
        project.save()
        process_speech_to_text.delay(speechtotext.id, input_file=file_path, lang=lang,
                                     token=user.device_token)

        return speechtotext
    except Exception as e:
        delete_project_with_files(project)
        raise e


def summary_article_audio_func(project, user):
    youtube_link = project.input_text
    if youtube_link:
        youtube_file = download_audio_from_youtube(youtube_link)
        if youtube_file:
            with open(youtube_file, 'rb') as f:
                project.input_file.save(f"{project.id}_audio.mp3", File(f))
            project.save()
            file_path = project.input_file.path
            if os.path.exists(youtube_file):
                os.remove(youtube_file)
        else:
            raise ValidationError("Could not download audio from YouTube.", code="youtube_link")
    else:
        file_path = project.input_file.path
        logger.debug(
            f'Attempting to open file: {file_path}+++++++++++++++++++++++++++++\n++++++++++++++++++++++\n++++++++++++++++++++++++++')
    file_size = os.path.getsize(file_path)

    if file_size > 1024 * 1024 * 1024:  # 1 GB
        raise ValidationError("File size must be max 1 gb ", code="incorrect_size")
    if not file_path.endswith(('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')):
        if file_path.endswith(('.flac', '.aac', '.ogg', '.avi', '.mov', '.wmv',
                               '.mkv', '.flv', '.3gp')):
            file_path = convert_to_wav_v2(file_path)
        else:
            raise ValidationError("Incorrect file format. choose one: audio or video", code="incorrect_format")
    project.loading = True
    project.save()
    duration = get_audio_duration(input_file=file_path)
    process_summary_article.delay(project.id, user.id, audio_filename=file_path, duration=duration)

    return project
