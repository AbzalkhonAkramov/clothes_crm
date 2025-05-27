from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'lang', 'credit_sums', 'credit_seconds', 'used_sums', 'used_seconds', 'device_token')


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'telegram_id', 'tokens', 'device_token')
        read_only_fields = ('id', 'tokens')

    def create(self, validated_data):
        telegram_id = validated_data.get('telegram_id')
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': telegram_id,
                'email': f"{telegram_id}@telegram.org",
                'telegram_id': telegram_id,
                'first_name': validated_data.get('first_name', ''),
                'last_name': validated_data.get('last_name', ''),
                'credit_sums': 6000,
                'credit_seconds': 600,
                'password': make_password(telegram_id),
                'lang': User.LangChoices.UZ,
                'device_token': validated_data.get('device_token', None),
                'is_accepted_privacy': False,
            }
        )
        return user

    def to_representation(self, instance):
        data = super(UserModelSerializer, self).to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['tokens'] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
        return data



class PasswordCheckSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get("phone")
        password = data.get("password")

        user = User.objects.filter(phone=phone).first()
        if not user:
            raise ValidationError("User not found",code="user_not_fount")

        if not check_password(password, user.password):
            raise ValidationError("Password error",code="user_not_fount")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "telegram_id": user.telegram_id,
            "tokens": {
                "refresh": str(refresh),
                "access": access_token
            },
            "device_token": user.device_token if user.device_token else None
        }

