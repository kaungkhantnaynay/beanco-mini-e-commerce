from typing import cast

import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.accounts.factories import UserFactory
from apps.accounts.models import User
from apps.orders.admin import AddressAdmin, OrderAdmin, OrderItemAdmin
from apps.orders.factories import AddressFactory, OrderFactory, OrderItemFactory
from apps.orders.models import Address, Order, OrderItem


def test_order_models_are_registered_with_controlled_admin_actions() -> None:
    assert {Address, Order, OrderItem}.issubset(admin.site._registry)
    model_admin = OrderAdmin(Order, admin.site)
    assert {
        "mark_confirmed",
        "mark_fulfilling",
        "mark_shipped",
        "mark_delivered",
        "mark_cancelled",
    }.issubset(model_admin.actions)
    assert "status" in model_admin.readonly_fields


@pytest.mark.django_db
def test_order_admin_disallows_manual_add_and_delete() -> None:
    order = cast(Order, OrderFactory())
    request = RequestFactory().get("/admin/orders/order/")
    request.user = cast(User, UserFactory(is_staff=True))
    model_admin = OrderAdmin(Order, admin.site)

    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_delete_permission(request, order)


@pytest.mark.django_db
def test_snapshot_admins_are_read_only() -> None:
    address = cast(Address, AddressFactory())
    item = cast(OrderItem, OrderItemFactory())
    request = RequestFactory().get("/admin/orders/address/")
    request.user = cast(User, UserFactory(is_staff=True))
    address_admin = AddressAdmin(Address, admin.site)
    item_admin = OrderItemAdmin(OrderItem, admin.site)

    assert address_admin.has_change_permission(request, address)
    assert item_admin.has_change_permission(request, item)
    assert not address_admin.has_add_permission(request)
    assert not item_admin.has_delete_permission(request, item)
    assert set(address_admin.get_readonly_fields(request, address)) == {
        field.name for field in Address._meta.fields
    }
