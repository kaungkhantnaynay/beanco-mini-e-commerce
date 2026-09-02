import threading
from decimal import Decimal
from typing import cast

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from rest_framework.exceptions import ValidationError

from apps.carts.factories import CartFactory, CartItemFactory
from apps.carts.models import Cart
from apps.catalog.factories import ProductVariantFactory
from apps.catalog.models import ProductVariant
from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord, InventoryTransaction
from apps.orders.factories import AddressFactory, OrderFactory, OrderItemFactory
from apps.orders.models import Address, Order, OrderItem
from apps.orders.services import create_order, transition_order


def service_address() -> dict[str, str]:
    return {
        "full_name": "Mali Example",
        "phone": "0812345678",
        "address_line_1": "99 Fictional Coffee Lane",
        "address_line_2": "Unit 4B",
        "subdistrict": "Khlong Tan Nuea",
        "district": "Watthana",
        "province": "Bangkok",
        "postal_code": "10110",
        "country_code": "TH",
    }


@pytest.mark.django_db
def test_address_and_order_item_snapshots_are_immutable() -> None:
    address = cast(Address, AddressFactory())
    item = cast(OrderItem, OrderItemFactory())
    address.province = "Changed"
    item.unit_price = Decimal("1.00")

    with pytest.raises(DjangoValidationError):
        address.save()
    with pytest.raises(DjangoValidationError):
        Address.objects.filter(pk=address.pk).update(province="Changed")
    with pytest.raises(DjangoValidationError):
        item.save()
    with pytest.raises(DjangoValidationError):
        OrderItem.objects.filter(pk=item.pk).update(unit_price=Decimal("1.00"))
    with pytest.raises(DjangoValidationError):
        item.delete()


@pytest.mark.django_db
def test_order_commercial_fields_are_immutable_but_status_is_service_controlled() -> None:
    order = cast(Order, OrderFactory())
    order.total = Decimal("1.00")

    with pytest.raises(DjangoValidationError):
        order.save()
    with pytest.raises(DjangoValidationError):
        Order.objects.filter(pk=order.pk).update(total=Decimal("1.00"))
    with pytest.raises(DjangoValidationError):
        order.delete()

    order.refresh_from_db()
    order.status = Order.Status.SHIPPED
    with pytest.raises(DjangoValidationError):
        order.save()
    with pytest.raises(DjangoValidationError):
        Order.objects.filter(pk=order.pk).update(status=Order.Status.CONFIRMED)


@pytest.mark.django_db
def test_controlled_status_transitions_and_cancellation_restore_stock_once() -> None:
    variant = cast(ProductVariant, ProductVariantFactory())
    inventory = cast(
        InventoryRecord,
        InventoryRecordFactory(variant=variant, available_quantity=8),
    )
    order = cast(Order, OrderFactory(status=Order.Status.AWAITING_PAYMENT))
    OrderItemFactory(order=order, variant=variant, quantity=2)

    cancelled = transition_order(order=order, target_status=Order.Status.CANCELLED)

    assert cancelled.status == Order.Status.CANCELLED
    assert cancelled.stock_restored is True
    inventory.refresh_from_db()
    assert inventory.available_quantity == 10
    restored = InventoryTransaction.objects.get(reason=InventoryTransaction.Reason.CANCELLATION)
    assert restored.quantity_change == 2
    with pytest.raises(DjangoValidationError):
        transition_order(order=cancelled, target_status=Order.Status.CANCELLED)
    inventory.refresh_from_db()
    assert inventory.available_quantity == 10


@pytest.mark.django_db
def test_status_machine_rejects_skips_and_allows_fulfillment_sequence() -> None:
    order = cast(Order, OrderFactory())
    with pytest.raises(DjangoValidationError):
        transition_order(order=order, target_status=Order.Status.SHIPPED)

    for target in (
        Order.Status.CONFIRMED,
        Order.Status.FULFILLING,
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
    ):
        order = transition_order(order=order, target_status=target)
    assert order.status == Order.Status.DELIVERED


@pytest.mark.skipif(connection.vendor != "postgresql", reason="requires PostgreSQL row locks")
@pytest.mark.django_db(transaction=True)
def test_concurrent_orders_cannot_oversell_tracked_stock() -> None:
    variant = cast(ProductVariant, ProductVariantFactory(sku="CONCURRENT"))
    InventoryRecordFactory(variant=variant, available_quantity=1)
    carts = [cast(Cart, CartFactory()) for _ in range(2)]
    for cart in carts:
        CartItemFactory(cart=cart, variant=variant, quantity=1)

    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def place_order(cart_id: int, key: str) -> None:
        close_old_connections()
        try:
            barrier.wait(timeout=5)
            create_order(
                cart=Cart.objects.get(pk=cart_id),
                idempotency_key=key,
                customer_email=f"{key}@example.test",
                shipping_address=service_address(),
                shipping_method="standard_th",
            )
            outcomes.append("created")
        except ValidationError:
            outcomes.append("rejected")
        finally:
            close_old_connections()

    threads = [
        threading.Thread(target=place_order, args=(cart.pk, f"concurrency-key-{index}"))
        for index, cart in enumerate(carts)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not any(thread.is_alive() for thread in threads)
    assert sorted(outcomes) == ["created", "rejected"]
    assert Order.objects.count() == 1
    inventory = InventoryRecord.objects.get(variant=variant)
    assert inventory.available_quantity == 0
    assert InventoryTransaction.objects.filter(reason=InventoryTransaction.Reason.SALE).count() == 1


@pytest.mark.django_db
def test_order_total_database_constraint() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        OrderFactory(subtotal=Decimal("850.00"), total=Decimal("1.00"))
