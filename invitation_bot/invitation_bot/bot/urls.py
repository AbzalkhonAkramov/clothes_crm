from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fonts', views.FontViewSet)
router.register(r'templates', views.TemplateViewSet)
router.register(r'icons', views.IconViewSet)
router.register(r'users', views.TelegramUserViewSet)
router.register(r'invitations', views.InvitationViewSet)
router.register(r'sessions', views.UserSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]