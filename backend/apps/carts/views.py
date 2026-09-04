from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.api.serializers import ApiErrorSerializer

from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    CheckoutPreviewInputSerializer,
    CheckoutPreviewSerializer,
    UpdateCartItemSerializer,
)
from .services import (
    CartAccess,
    add_cart_item,
    build_checkout_preview,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item,
)


class CartAPIView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "carts"

    def get_access(self, request: Request) -> CartAccess:
        return get_or_create_cart(
            request.COOKIES.get(settings.CART_COOKIE_NAME),
            request.user if request.user.is_authenticated else None,
        )

    def response_with_cookie(self, response: Response, access: CartAccess) -> Response:
        if access.set_cookie:
            response.set_cookie(
                settings.CART_COOKIE_NAME,
                access.token,
                max_age=settings.CART_COOKIE_MAX_AGE,
                httponly=True,
                secure=settings.CART_COOKIE_SECURE,
                samesite="Lax",
                path="/api/v1/",
            )
        return response


class CartView(CartAPIView):
    @extend_schema(responses={200: CartSerializer})
    def get(self, request: Request) -> Response:
        access = self.get_access(request)
        response = Response(CartSerializer(access.cart).data)
        return self.response_with_cookie(response, access)


class CartItemCreateView(CartAPIView):
    @extend_schema(
        request=AddCartItemSerializer,
        responses={200: CartSerializer, 201: CartSerializer, 400: ApiErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        access = self.get_access(request)
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, created = add_cart_item(cart=access.cart, **serializer.validated_data)
        access.cart.refresh_from_db()
        response = Response(
            CartSerializer(access.cart).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        return self.response_with_cookie(response, access)


class CartItemDetailView(CartAPIView):
    @extend_schema(
        request=UpdateCartItemSerializer,
        responses={200: CartSerializer, 400: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    def patch(self, request: Request, public_id: str) -> Response:
        access = self.get_access(request)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_cart_item(cart=access.cart, public_id=public_id, **serializer.validated_data)
        access.cart.refresh_from_db()
        response = Response(CartSerializer(access.cart).data)
        return self.response_with_cookie(response, access)

    @extend_schema(responses={204: None, 404: ApiErrorSerializer})
    def delete(self, request: Request, public_id: str) -> Response:
        access = self.get_access(request)
        remove_cart_item(cart=access.cart, public_id=public_id)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        return self.response_with_cookie(response, access)


class CheckoutPreviewView(CartAPIView):
    throttle_scope = "checkout"

    @extend_schema(
        request=CheckoutPreviewInputSerializer,
        responses={200: CheckoutPreviewSerializer, 400: ApiErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        access = self.get_access(request)
        serializer = CheckoutPreviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        preview = build_checkout_preview(
            cart=access.cart,
            shipping_address=serializer.validated_data["shipping_address"],
        )
        response = Response(CheckoutPreviewSerializer(preview).data)
        return self.response_with_cookie(response, access)
