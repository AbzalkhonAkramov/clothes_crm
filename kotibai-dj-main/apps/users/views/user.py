from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

from users.models import User, OrderPayment
from users.serializers.related import UserCreditsUpdateSerializer, OrderPaymentModelSerializer
from users.serializers.user import UserModelSerializer, UserSerializer, \
    PasswordCheckSerializer
from rest_framework.permissions import AllowAny


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super().post(request, *args, **kwargs)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        device_token = request.data.get('device_token', None)
        if device_token:
            user.device_token = device_token
            user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    def get(self, request):
        user = User.objects.get(username='admin')
        refresh = RefreshToken.for_user(user)
        data = {}
        data['tokens'] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
        return Response(data)


class UserCreditsUpdateView(generics.CreateAPIView):
    schema = None
    queryset = User.objects.all()
    serializer_class = UserCreditsUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telegram_id = serializer.validated_data['telegram_id']
        credit_sums = serializer.validated_data['credit_sums']
        user = User.objects.filter(telegram_id=int(telegram_id / 2)).first()
        if user is None:
            return Response('User does not exist', status=status.HTTP_404_NOT_FOUND)

        user.credit_sums = user.credit_sums - credit_sums
        user.credit_seconds = user.credit_seconds - int(credit_sums / 10)
        user.used_sums = user.used_sums + credit_sums
        user.used_seconds = user.used_seconds + int(credit_sums / 10)
        user.save()
        return Response('User updated successfully', status=status.HTTP_200_OK)


class OrderPaymentCreateAPIView(CreateAPIView):
    serializer_class = OrderPaymentModelSerializer
    queryset = OrderPayment.objects.all()
    permission_classes = (IsAuthenticated,)


class PasswordCheckView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)

