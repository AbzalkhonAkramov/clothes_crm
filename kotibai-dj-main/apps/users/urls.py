from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views.user import UserRegisterAPIView,PasswordCheckView, UserProfileView, GetToken, UserCreditsUpdateView, OrderPaymentCreateAPIView
from .views.v2 import ProjectViewSet, SummaryCreateView, ArticleCreateView, TranslateCreateView, SpeechtotextCreateView, \
    GetUzbekVoiceText, SpeechtotextForBotCreateApiView, GetUzbekVoiceForOther

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('projects/<int:project_id>/speechtotext/<int:pk>', SpeechtotextCreateView.as_view()),
    path('projects/<int:project_id>/summary/', SummaryCreateView.as_view({'get': 'list', 'post': 'create'})),
    path('projects/<int:project_id>/summary/<int:pk>', SummaryCreateView.as_view({'patch': 'partial_update'})),
    path('projects/<int:project_id>/article/', ArticleCreateView.as_view({'get': 'list', 'post': 'create'})),
    path('projects/<int:project_id>/article/<int:pk>', ArticleCreateView.as_view({'patch': 'partial_update'})),
    path('projects/<int:project_id>/translate/', TranslateCreateView.as_view({'get': 'list', 'post': 'create'})),
    path('projects/<int:project_id>/translate/<int:pk>', TranslateCreateView.as_view({'patch': 'partial_update'})),
    path('update/credits', UserCreditsUpdateView.as_view(), name='update-credits'),
    path('auth/check-password/', PasswordCheckView.as_view(), name='check-password'),
    path('auth/telegram', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/profile', UserProfileView.as_view(), name='user-profile'),
    path('auth/get-token', GetToken.as_view(), name='user-token'),
    path('order-payment', OrderPaymentCreateAPIView.as_view(), name='user-register'),
    path('get-uzbek-voice-text', GetUzbekVoiceText.as_view(), name='get-uzbek-voice-text'),
    path('get-uzbek-voice-for-others', GetUzbekVoiceForOther.as_view(), name='get-uzbek-voice-for-others'),
    path('stt-create-for-bot', SpeechtotextForBotCreateApiView.as_view(), name='stt-create-for-bot'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),

]
