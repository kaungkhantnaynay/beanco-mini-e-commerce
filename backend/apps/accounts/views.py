from typing import Any, cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.api.serializers import ApiErrorSerializer

from .models import User
from .notifications import send_password_reset_email, send_verification_email
from .serializers import (
    AccountSerializer,
    DetailSerializer,
    EmailTokenSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
)
from .tokens import email_verification_token

NEUTRAL_REGISTRATION_DETAIL = "If registration is available for this address, check your email."
NEUTRAL_RESET_DETAIL = "If an eligible account exists, password-reset instructions were sent."


class CsrfProtectedAPIView(APIView):
    permission_classes: tuple[type[BasePermission], ...] = (AllowAny,)

    def initial(self, request: Request, *args: object, **kwargs: object) -> None:
        super().initial(request, *args, **kwargs)
        SessionAuthentication().enforce_csrf(request)


def _user_from_uid(uid: str) -> User | None:
    try:
        return User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


class CsrfCookieView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(responses={200: DetailSerializer})
    def get(self, request: Request) -> Response:
        get_token(request._request)
        return Response({"detail": "CSRF cookie set."})


class RegistrationView(CsrfProtectedAPIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "registration"

    @extend_schema(
        request=RegistrationSerializer,
        responses={
            202: DetailSerializer,
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: dict[str, Any] = serializer.validated_data
        email = str(data["email"])
        password = str(data["password"])
        try:
            with transaction.atomic():
                user = User.objects.filter(email=email).first()
                if user is None:
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=str(data.get("first_name", "")).strip(),
                        last_name=str(data.get("last_name", "")).strip(),
                        is_active=False,
                    )
                    transaction.on_commit(lambda: send_verification_email(user))
                elif user.email_verified_at is None and not user.is_active:
                    transaction.on_commit(lambda: send_verification_email(user))
        except IntegrityError:
            pass
        return Response({"detail": NEUTRAL_REGISTRATION_DETAIL}, status=status.HTTP_202_ACCEPTED)


class EmailVerificationView(CsrfProtectedAPIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "account_auth"

    @extend_schema(
        request=EmailTokenSerializer,
        responses={200: DetailSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = EmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _user_from_uid(serializer.validated_data["uid"])
        if user is None or not email_verification_token.check_token(
            user, serializer.validated_data["token"]
        ):
            raise ValidationError({"token": ["This verification link is invalid or expired."]})
        user.email_verified_at = timezone.now()
        user.is_active = True
        user.save(update_fields=("email_verified_at", "is_active"))
        return Response({"detail": "Email verified. You can now sign in."})


class LoginView(CsrfProtectedAPIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "login"

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: AccountSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request._request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None or user.email_verified_at is None:
            raise AuthenticationFailed("Unable to sign in with those credentials.")
        login(request._request, user)
        return Response(AccountSerializer(user).data)


class LogoutView(CsrfProtectedAPIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={200: DetailSerializer, 401: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        logout(request._request)
        return Response({"detail": "Signed out."})


class CurrentAccountView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={200: AccountSerializer, 401: ApiErrorSerializer, 403: ApiErrorSerializer}
    )
    def get(self, request: Request) -> Response:
        return Response(AccountSerializer(cast(User, request.user)).data)


class PasswordResetRequestView(CsrfProtectedAPIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "password_reset"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            202: DetailSerializer,
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email=serializer.validated_data["email"],
            is_active=True,
            email_verified_at__isnull=False,
        ).first()
        if user is not None:
            transaction.on_commit(lambda: send_password_reset_email(user))
        return Response({"detail": NEUTRAL_RESET_DETAIL}, status=status.HTTP_202_ACCEPTED)


class PasswordResetConfirmView(CsrfProtectedAPIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "account_auth"

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: DetailSerializer,
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _user_from_uid(serializer.validated_data["uid"])
        if user is None or not default_token_generator.check_token(
            user, serializer.validated_data["token"]
        ):
            raise ValidationError({"token": ["This password-reset link is invalid or expired."]})
        try:
            validate_password(serializer.validated_data["new_password"], user)
        except DjangoValidationError as exc:
            raise ValidationError({"new_password": list(exc.messages)}) from exc
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=("password",))
        return Response({"detail": "Password updated. You can now sign in."})
