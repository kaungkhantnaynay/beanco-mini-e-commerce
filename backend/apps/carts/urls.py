from django.urls import path

from .views import CartItemCreateView, CartItemDetailView, CartView, CheckoutPreviewView

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart-detail"),
    path("cart/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path("cart/items/<uuid:public_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("checkout/preview/", CheckoutPreviewView.as_view(), name="checkout-preview"),
]
