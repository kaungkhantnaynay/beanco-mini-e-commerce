from typing import cast

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.api.serializers import ApiErrorSerializer
from apps.carts.views import CartAPIView

from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusSerializer
from .services import create_order, validate_idempotency_key


class OrderCreateView(CartAPIView):
    throttle_scope = "orders"

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "Idempotency-Key",
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Unique 16–128 character key for safely retrying order creation.",
            )
        ],
        request=OrderCreateSerializer,
        responses={
            200: OrderSerializer,
            201: OrderSerializer,
            400: ApiErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        access = self.get_access(request)
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = validate_idempotency_key(request.headers.get("Idempotency-Key"))
        order, created = create_order(
            cart=access.cart,
            idempotency_key=key,
            **serializer.validated_data,
        )
        response = Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        return self.response_with_cookie(response, access)


class OrderStatusView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "carts"

    @extend_schema(responses={200: OrderStatusSerializer, 404: ApiErrorSerializer})
    def get(self, request: Request, public_id: str) -> Response:
        try:
            order = Order.objects.get(public_id=public_id)
        except (Order.DoesNotExist, ValueError) as exc:
            raise NotFound("Order not found.") from exc
        return Response(OrderStatusSerializer(order).data)


class AccountOrderListView(ListAPIView[Order]):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderStatusSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Order.objects.filter(user_id=cast(int, self.request.user.pk)).order_by("-created_at")


class AccountOrderDetailView(RetrieveAPIView[Order]):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Order.objects.filter(user_id=cast(int, self.request.user.pk))
            .select_related("shipping_address")
            .prefetch_related("items")
        )
