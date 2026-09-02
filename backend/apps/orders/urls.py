from django.urls import path

from .views import OrderCreateView, OrderStatusView

urlpatterns = [
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<uuid:public_id>/status/", OrderStatusView.as_view(), name="order-status"),
]
