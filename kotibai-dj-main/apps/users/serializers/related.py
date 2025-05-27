from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault, HiddenField

from users.models.related import OrderPayment


class UserCreditsUpdateSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(required=True)
    credit_sums = serializers.IntegerField(required=True)


class OrderPaymentModelSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = OrderPayment
        fields = '__all__'
        read_only_fields = ('id', 'status', 'transaction_id')

    def create(self, validated_data):
        if validated_data['type'] == OrderPayment.PaymentChoices.PAYME:
            validated_data['amount'] *= 100
        return super().create(validated_data)
