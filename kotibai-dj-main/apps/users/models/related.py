from uuid import uuid4

from django.db import models
from django.db.models import TextChoices


class OrderPayment(models.Model):
    class PaymentChoices(TextChoices):
        CLICK = 'click', 'Click'
        PAYME = 'payme', 'Payme'
        TELEGRAM = 'telegram', 'Telegram'

    class StatusChoices(TextChoices):
        CREATED = 'created', 'Created'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        CANCEL = 'cancel', 'Cancel'

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    discount_amount = models.FloatField(null=True, blank=True)
    promocode = models.ForeignKey("users.PromoCode", on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=PaymentChoices.choices)
    transaction_id = models.UUIDField(default=uuid4)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.CREATED)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orderpayment'

    def __str__(self):
        return f"{self.user.first_name if self.user else self.id}"


class LangChoices(TextChoices):
    UZ = 'uz-UZ', 'Uzbek'
    EN = 'en-US', 'English'
    RU = 'ru-RU', 'Russian'
    RU_UZ = 'ru-uz', 'Russian-Uzbek'


class TypeChoices(TextChoices):
    ARTICLE = 'article', 'Article'
    INTERVIEW = 'interview', 'Interview'
    NEWS = 'news', 'News'
    REPORTAGE = 'reportage', 'Reportage'


class Project(models.Model):
    class ActionChoices(TextChoices):
        STT = 'stt', 'Speech To Text'
        SUMMARY = 'summary', 'Summary'
        ARTICLE = 'article', 'Article'
        TRANSLATE = 'translate', 'Translate'

    class OutputChoices(TextChoices):
        TEXT = 'text', 'Text'
        DOCX = 'docx', 'Docx'

    name = models.CharField(max_length=255)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
    action_type = models.CharField(max_length=30, choices=ActionChoices.choices)
    output_type = models.CharField(max_length=30, choices=OutputChoices.choices)
    input_file = models.FileField(max_length=255, blank=True, null=True)
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    article_type = models.CharField(max_length=30, choices=TypeChoices.choices, null=True, blank=True)
    loading = models.BooleanField(default=False, null=True, blank=True)
    input_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)


class Speechtotext(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.OneToOneField('users.Project', on_delete=models.CASCADE, related_name='stt')
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    file_duration = models.IntegerField(null=True, blank=True)
    voice_id = models.CharField(max_length=255, blank=True, null=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    output_docx = models.FileField(max_length=255, blank=True, null=True)
    output_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'speechtotext'

    def __str__(self):
        return self.project.name


class SpeechtotextForBot(models.Model):
    class SpeechtotextForBotChoices(TextChoices):
        STT = 'stt', 'Speech To Text'
        SUMMARY = 'summary', 'Summary'
        ARTICLE = 'article', 'Article'
        INTERVIEW = 'interview', 'Interview'
        NEWS = 'news', 'News'
        REPORTAGE = 'reportage', 'Reportage'

    voice_id = models.CharField(max_length=255)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    duration = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=30, choices=SpeechtotextForBotChoices.choices, null=True, blank=True)
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'speechtotextforbot'

    def __str__(self):
        return f"{self.user.first_name}--"


class Summary(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey('users.Project', on_delete=models.CASCADE, related_name='summary')
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    output_docx = models.FileField(max_length=255, blank=True, null=True)
    output_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.name


class Article(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey('users.Project', on_delete=models.CASCADE, related_name='article')
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    type = models.CharField(max_length=30, choices=TypeChoices.choices, null=True, blank=True)
    output_docx = models.FileField(max_length=255, blank=True, null=True)
    output_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.name


class Translate(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey('users.Project', on_delete=models.CASCADE, related_name='translate')
    lang = models.CharField(max_length=15, choices=LangChoices.choices, null=True, blank=True)
    output_docx = models.FileField(max_length=255, blank=True, null=True)
    output_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.name
