from typing import cast

from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.api.serializers import ApiErrorSerializer
from apps.carts.services import hash_cart_token
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer

from .providers import WebhookVerificationError, get_payment_provider
from .serializers import CheckoutSessionSerializer, WebhookResponseSerializer
from .services import (
    cancel_customer_order,
    create_checkout_session,
    get_order_for_payment,
    process_webhook_event,
)


class CheckoutSessionCreateView(APIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "payments"

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "Idempotency-Key", OpenApiTypes.STR, OpenApiParameter.HEADER, required=True
            )
        ],
        request=None,
        responses={
            200: CheckoutSessionSerializer,
            201: CheckoutSessionSerializer,
            400: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def post(self, request: Request, public_id: str) -> Response:
        raw_token = request.COOKIES.get(settings.CART_COOKIE_NAME)
        order = get_order_for_payment(
            public_id=public_id,
            cart_token_hash=hash_cart_token(raw_token) if raw_token else None,
            user_id=request.user.pk if request.user.is_authenticated else None,
        )
        attempt, created = create_checkout_session(
            order=order,
            idempotency_key=request.headers.get("Idempotency-Key", ""),
            provider=get_payment_provider(),
        )
        return Response(
            CheckoutSessionSerializer(attempt).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class StripeWebhookView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        request=bytes,
        responses={200: WebhookResponseSerializer, 400: ApiErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        signature = request.headers.get("Stripe-Signature", "")
        try:
            event = get_payment_provider().construct_event(
                payload=request.body, signature=signature
            )
        except WebhookVerificationError:
            return Response(
                {"code": "invalid_signature", "detail": "Invalid webhook signature.", "fields": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        processed = process_webhook_event(event)
        return Response({"received": True, "duplicate": not processed})


class CustomerOrderCancellationView(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "payments"

    @extend_schema(
        request=None,
        responses={200: OrderSerializer, 400: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    def post(self, request: Request, public_id: str) -> Response:
        try:
            order = Order.objects.get(public_id=public_id, user_id=cast(int, request.user.pk))
        except (Order.DoesNotExist, ValueError) as exc:
            raise NotFound("Order not found.") from exc
        cancelled = cancel_customer_order(
            order=order,
            actor=request.user,
            provider=get_payment_provider(),
        )
        return Response(OrderSerializer(cancelled).data)
