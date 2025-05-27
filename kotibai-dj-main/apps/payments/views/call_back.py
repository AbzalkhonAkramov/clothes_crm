from decimal import Decimal

from django.http import HttpResponseRedirect
from payme.views import MerchantAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.utils import payment_status_approval
from root.settings import TIME_PRICES, PAYME
from users.models import OrderPayment, PromoCodeUsage
from users.utils import send_message, convert_credits_to_time, is_valid_uuid, loaded_yaml


class PaymeCallBackAPIView(MerchantAPIView):
    def create_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"create_transaction for order_id: {order_id}, response: {action}")
        order: OrderPayment = OrderPayment.objects.filter(id=order_id).first()
        if order:
            order.status = OrderPayment.StatusChoices.PENDING
            order.save()

    def perform_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"perform_transaction for order_id: {order_id}, response: {action}")
        order: OrderPayment = OrderPayment.objects.filter(id=order_id).first()
        if order:
            order.status = OrderPayment.StatusChoices.PAID
            prices = {
                36000: 3600,
                100000: 10800,
                200000: 25200,
                500000: 61200
            }
            amount = int(int(order.amount) // 100)
            print('amount: ', amount)
            user = order.user
            print('used_seconds before payment: ', user.credit_seconds)
            seconds = Decimal(prices.get(amount, amount / TIME_PRICES['second']))
            user.credit_seconds += seconds
            user.credit_sums += seconds * TIME_PRICES['second']
            user.save()
            order.save()
            if order.promocode:
                promocode_usage = PromoCodeUsage.objects.filter(id=order.promocode.id).first()
                if promocode_usage:
                    promocode_usage.usage_count = promocode_usage.usage_count + 1
                    promocode_usage.save()
                else:
                    promocode_usage = PromoCodeUsage.objects.create(promo_code=order.promocode, user=user,
                                                                    usage_count=1)
            time_traffic = convert_credits_to_time(user.credit_seconds, user.lang)
            message_template = loaded_yaml['payment_confirmation'].get(user.lang)
            text = message_template['message'].format(
                payment_date=str(order.updated_at).split('.')[0], payment_amount=amount,
                time_traffic=time_traffic)
            send_message(user.telegram_id, text)

    def cancel_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"cancel_transaction for order_id: {order_id}, response: {action}")
        order: OrderPayment = OrderPayment.objects.filter(id=order_id).first()
        if order:
            order.status = OrderPayment.StatusChoices.CANCEL
            order.save()
            user = order.user
            message_template = loaded_yaml['payment_cancelled'].get(user.lang)
            text = message_template['message']
            send_message(user.telegram_id,
                         text
                         )


class ClickCallBackAPIView(APIView):

    def get(self, request, *args, **kwargs):
        transaction_id = request.query_params.get('transaction_id')
        payment_id = request.query_params.get('transaction_id')
        current_date = request.query_params.get('current_date')
        if not (transaction_id or payment_id):
            raise ValidationError("transaction_id is required")
        payment_status_approval(transaction_id, payment_id, current_date)
        return HttpResponseRedirect(PAYME['PAYME_CALL_BACK_URL'].replace('{transaction_id}', str(transaction_id)))


class OrderStatusCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        transaction_id = request.query_params.get('transaction_id')
        if not transaction_id:
            raise ValidationError("transaction_id is required")
        if not is_valid_uuid(transaction_id):
            raise ValidationError("transaction_id is not valid")
        order = OrderPayment.objects.filter(transaction_id=transaction_id).first()
        if not order:
            return Response("Order not found", status=404)
        if order.user != request.user:
            return Response("Order not found", status=404)
        return Response({"status": order.status})
