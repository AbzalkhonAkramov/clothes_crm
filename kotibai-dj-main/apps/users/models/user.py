from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    class TypeChoices(TextChoices):
        GOOGLE = 'google', 'Google'
        TELEGRAM = 'telegram', 'Telegram'

    class LangChoices(TextChoices):
        UZ = 'uz', 'Uzbek'
        EN = 'en', 'English'
        RU = 'ru', 'Russian'

    username_validator = UnicodeUsernameValidator()
    first_name = models.CharField(_("first name"), max_length=150, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, null=True, blank=True)
    telegram_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    lang = models.CharField(max_length=15, choices=LangChoices.choices, blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    credit_sums = models.DecimalField(max_digits=10, decimal_places=2, default=600)
    credit_seconds = models.DecimalField(max_digits=10, decimal_places=2, default=60)
    used_sums = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    used_seconds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_accepted_privacy= models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # email = models.EmailField(unique=True, max_length=255, blank=True, null=True)

    username = models.CharField(
        _("username"),

        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    login_type = models.CharField(max_length=20, choices=TypeChoices.choices, blank=True, null=True)
    device_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'users'

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def __str__(self):
        return f"{self.first_name} - {self.last_name} "


class ChannelSubscribes(models.Model):
    user = models.ForeignKey(User, related_name="channels", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_subscribe = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.created_at}"