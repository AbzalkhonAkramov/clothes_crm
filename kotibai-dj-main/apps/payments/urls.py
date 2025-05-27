from django.urls import path

from payments.views import PaymeCallBackAPIView, GeneratePayLinkAPIView, GenerateClickPayLinkAPIView, ClickCallBackAPIView, OrderStatusCheckAPIView

urlpatterns = [
    path('click/pay-link/', GenerateClickPayLinkAPIView.as_view(), name='generate-click-pay-link'),
    path('click/endpoint/', ClickCallBackAPIView.as_view(), name='click-callback'),
    path('payme/pay-link/', GeneratePayLinkAPIView.as_view(), name='generate-payme-pay-link'),
    path('merchant/', PaymeCallBackAPIView.as_view(), name='merchant-callback'),
    path('payment/status-check', OrderStatusCheckAPIView.as_view(), name='status-check')
]
