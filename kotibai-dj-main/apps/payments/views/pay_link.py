from drf_yasg.utils import swagger_auto_schema
from payme.methods.generate_link import GeneratePayLink
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.click import ClickPay
from payments.serializers import GeneratePayLinkSerializer, GenerateClickPayLinkSerializer
from root.settings import PAYME
from tasks import payment_status_check


class GeneratePayLinkAPIView(APIView):
    @swagger_auto_schema(
        request_body=GeneratePayLinkSerializer,
        responses={200: "{'pay_link': str}"}
    )
    def post(self, request, *args, **kwargs):
        """
        Generate a payment link for the given order ID and amount.

        Request parameters:
            - order_id (int): The ID of the order to generate a payment link for.
            - amount (int): The amount of the payment.

        Example request:
            curl -X POST \
                'http://your-host/shop/pay-link/' \
                --header 'Content-Type: application/json' \
                --data-raw '{
                "order_id": 999,
            }'

        Example response:
            {
                "pay_link": "http://payme-api-gateway.uz/bT0jcmJmZk1vNVJPQFFoP05GcHJtWnNHeH"
            }
        """
        serializer = GeneratePayLinkSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        order = serializer.validated_data['order_id']
        pay_link = GeneratePayLink(order.id, order.amount, PAYME['PAYME_CALL_BACK_URL'].replace('{transaction_id}', str(order.transaction_id))).generate_link()

        return Response({"pay_link": pay_link})


class GenerateClickPayLinkAPIView(APIView):
    @swagger_auto_schema(
        request_body=GenerateClickPayLinkSerializer,
        responses={200: "{'pay_link': str}"}
    )
    def post(self, request, *args, **kwargs):
        """
        Generate a payment link for the given order ID

        Request parameters:
            - order_id (int): The ID of the order to generate a payment link for.
        Example request:
            curl -X POST \
                'http://your-host/shop/pay-link/' \
                --header 'Content-Type: application/json' \
                --data-raw '{
                "order_id": 999,
            }'

        Example response:
            {
                "pay_link": "http://click-api-gateway.uz/bT0jcmJmZk1vNVJPQFFoP05GcHJtWnNHeH"
            }
        """
        serializer = GenerateClickPayLinkSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        data = serializer.validated_data
        order = serializer.validated_data['order_id']

        click = ClickPay()
        # endpoint_url = request.build_absolute_uri(reverse('click-callback'))
        pay_link = click.create_redirect_payment(order.amount, data['card_type'], PAYME['PAYME_CALL_BACK_URL'].replace('{transaction_id}', str(order.transaction_id)),
                                                 order.transaction_id)
        payment_status_check.apply_async(args=[order.transaction_id], countdown=20)
        return Response({"pay_link": pay_link})
