from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Font, Template, Icon, TelegramUser, Invitation, UserSession
from .serializers import (
    FontSerializer, TemplateSerializer, IconSerializer,
    TelegramUserSerializer, InvitationSerializer, UserSessionSerializer
)
from .serveice import generate_invitation_image




class FontViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Font.objects.all()
    serializer_class = FontSerializer
    permission_classes = [permissions.IsAuthenticated]


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.filter(is_active=True)
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class IconViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icon.objects.filter(is_active=True)
    serializer_class = IconSerializer
    permission_classes = [permissions.IsAuthenticated]


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'telegram_id'

    @action(detail=True, methods=['get'])
    def invitations(self, request, telegram_id=None):
        user = self.get_object()
        invitations = Invitation.objects.filter(user=user)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate_image(self, request, pk=None):
        invitation = self.get_object()
        success, message = generate_invitation_image(invitation)

        if success:
            return Response({"message": "Invitation image generated successfully",
                             "image_url": invitation.final_image.url},
                            status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class UserSessionViewSet(viewsets.ModelViewSet):
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__telegram_id'

    def get_object(self):
        telegram_id = self.kwargs.get('user__telegram_id')
        return get_object_or_404(UserSession, user__telegram_id=telegram_id)