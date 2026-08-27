from typing import cast

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.api.serializers import ApiErrorSerializer

from .models import NewsletterSubscription, PartnershipInquiry
from .notifications import send_inquiry_notifications, send_subscription_confirmation
from .serializers import (
    NewsletterSubscriptionSerializer,
    PartnershipInquirySerializer,
    SubmissionResponseSerializer,
)


class PartnershipInquiryCreateView(GenericAPIView[PartnershipInquiry]):
    serializer_class = PartnershipInquirySerializer
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "inquiries"

    @extend_schema(
        request=PartnershipInquirySerializer,
        responses={
            201: SubmissionResponseSerializer,
            400: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = cast(PartnershipInquirySerializer, self.get_serializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            inquiry = serializer.save()
            transaction.on_commit(lambda: send_inquiry_notifications(inquiry))
        return Response(
            {"detail": "Your inquiry has been received."}, status=status.HTTP_201_CREATED
        )


class NewsletterSubscriptionCreateView(GenericAPIView[NewsletterSubscription]):
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "newsletter"

    @extend_schema(
        request=NewsletterSubscriptionSerializer,
        responses={
            202: SubmissionResponseSerializer,
            400: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = cast(NewsletterSubscriptionSerializer, self.get_serializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            subscription = serializer.save()
            if serializer.should_notify:
                transaction.on_commit(lambda: send_subscription_confirmation(subscription))
        return Response(
            {"detail": "If eligible, this address is subscribed."},
            status=status.HTTP_202_ACCEPTED,
        )
