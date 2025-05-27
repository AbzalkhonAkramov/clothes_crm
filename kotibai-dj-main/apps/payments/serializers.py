from rest_framework import serializers

from users.models import OrderPayment


class GeneratePayLinkSerializer(serializers.Serializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=OrderPayment.objects.all())
    # amount = serializers.IntegerField()


class GenerateClickPayLinkSerializer(serializers.Serializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=OrderPayment.objects.all())
    # amount = serializers.IntegerField()
    card_type = serializers.CharField()
