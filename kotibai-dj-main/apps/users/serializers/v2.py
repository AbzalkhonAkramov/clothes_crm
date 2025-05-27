from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import HiddenField, CurrentUserDefault

from users.models import Speechtotext
from users.models.related import Summary, Article, Translate, Project, SpeechtotextForBot
from users.utils.base_func import stt_create_and_process, process_project_action, summary_article_audio_func


class SpeechtotextSerializer(serializers.ModelSerializer):
    LANG_CHOICES = [
        ('uz-UZ', 'Uzbek'),
        ('en-US', 'English'),
        ('ru-RU', 'Russian'),
        ('ru-uz', 'Russian-Uzbek'),
    ]
    lang = serializers.ChoiceField(choices=LANG_CHOICES)

    class Meta:
        model = Speechtotext
        fields = '__all__'
        read_only_fields = ['user', 'project', 'output_docx', 'output_text', 'voice_id', 'file_duration', ]

    def get_output_docx(self, obj):
        request = self.context.get('request')
        if request:
            domain = 'https://api.kotibai.uz'
            return f"{domain}/media/{obj.output_docx}"
        return obj.output_docx


class SpeechtotextForBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechtotextForBot
        fields = ('id', 'voice_id', 'user', 'duration', 'type', 'lang')
        read_only_fields = ('id',)


class SummarySerializer(serializers.ModelSerializer):
    LANG_CHOICES = [
        ('uz-UZ', 'Uzbek'),
        ('en-US', 'English'),
        ('ru-RU', 'Russian'),
        ('ru-uz', 'Russian-Uzbek'),
    ]
    lang = serializers.ChoiceField(choices=LANG_CHOICES)

    class Meta:
        model = Summary
        fields = '__all__'
        read_only_fields = ['user', 'project', 'output_docx']

    def get_output_docx(self, obj):
        request = self.context.get('request')
        if request:
            domain = 'https://api.kotibai.uz'
            return f"{domain}/media/{obj.output_docx}"
        return obj.output_docx


class ArticleSerializer(serializers.ModelSerializer):
    LANG_CHOICES = [
        ('uz-UZ', 'Uzbek'),
        ('en-US', 'English'),
        ('ru-RU', 'Russian'),
        ('ru-uz', 'Russian-Uzbek'),
    ]
    lang = serializers.ChoiceField(choices=LANG_CHOICES)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['user', 'project', 'output_docx']

    def get_output_docx(self, obj):
        request = self.context.get('request')
        if request:
            domain = 'https://api.kotibai.uz'
            return f"{domain}/media/{obj.output_docx}"
        return obj.output_docx


class TranslateSerializer(serializers.ModelSerializer):
    LANG_CHOICES = [
        ('uz-UZ', 'Uzbek'),
        ('en-US', 'English'),
        ('ru-RU', 'Russian'),
        ('ru-uz', 'Russian-Uzbek'),
    ]
    lang = serializers.ChoiceField(choices=LANG_CHOICES)

    class Meta:
        model = Translate
        fields = '__all__'
        read_only_fields = ['user', 'project', 'output_docx']

    def get_output_docx(self, obj):
        request = self.context.get('request')
        if request:
            domain = 'https://api.kotibai.uz'
            return f"{domain}/media/{obj.output_docx}"
        return obj.output_docx


class ProjectSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    stt = SpeechtotextSerializer(read_only=True)
    summary = SummarySerializer(many=True, read_only=True)
    article = ArticleSerializer(many=True, read_only=True)
    translate = TranslateSerializer(many=True, read_only=True)
    LANG_CHOICES = [
        ('uz-UZ', 'Uzbek'),
        ('en-US', 'English'),
        ('ru-RU', 'Russian'),
        ('ru-uz', 'Russian-Uzbek'),
    ]

    Article_Choices = [
        ('article', 'Article'),
        ('interview', 'Interview'),
        ('news', 'News'),
        ('reportage', 'Reportage')
    ]
    Input_Choices = [
        ('audio_video', 'Audio-Video'),
        ('yt_link', 'YT-Link'),
        ('site_link', 'Site-Link'),
        ('text', 'Text'),
        ('docx', 'Docx')
    ]

    lang = serializers.ChoiceField(choices=LANG_CHOICES)
    audio_lang = serializers.ChoiceField(choices=LANG_CHOICES, write_only=True, required=False)
    article_type = serializers.ChoiceField(choices=Article_Choices, write_only=True, required=False)
    input_type = serializers.ChoiceField(choices=Input_Choices, write_only=True, required=False)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['loading']

    def create(self, validated_data):
        action_type = validated_data.get('action_type', None)
        lang = validated_data.get('lang', None)
        audio_lang = validated_data.pop('audio_lang', None)
        if lang not in ("uz-UZ", "ru-RU", "en-US", "ru-uz"):
            raise ValidationError("Invalid language: choose one: uz-UZ, ru-RU, en-US, ru-uz", code="invalid_lang")
        article_type = validated_data.get('article_type', None)
        input_type = validated_data.pop('input_type', None)
        input_file = validated_data.get('input_file', None)
        if input_type == 'audio_video' and input_file is None:
            raise ValidationError("Fayl topilmadi v2", code="file_not_found")
        user = validated_data.get('user')

        project = super().create(validated_data)
        if action_type == Project.ActionChoices.STT:
            stt_create_and_process(project, user, lang)
        elif input_type in (
        'audio_video', 'yt_link') and action_type != Project.ActionChoices.STT:
            summary_article_audio_func(project=project, user=user)
        elif input_type in ('audio_video', 'yt_link') and action_type != Project.ActionChoices.STT:
            stt_create_and_process(project, user, audio_lang)

        else:
            process_project_action(project, user, lang, article_type, input_type)
        return project

    def update(self, instance, validated_data):
        validated_data.pop('input_type', None)
        validated_data.pop('audio_lang', None)
        return super().update(instance, validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')
