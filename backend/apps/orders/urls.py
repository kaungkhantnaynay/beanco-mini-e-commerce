from django.urls import path

from .views import AccountOrderDetailView, AccountOrderListView, OrderCreateView, OrderStatusView

urlpatterns = [
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<uuid:public_id>/status/", OrderStatusView.as_view(), name="order-status"),
    path("account/orders/", AccountOrderListView.as_view(), name="account-order-list"),
    path(
        "account/orders/<uuid:public_id>/",
        AccountOrderDetailView.as_view(),
        name="account-order-detail",
    ),
]
