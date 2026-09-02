import hashlib
from decimal import Decimal

import factory

from apps.carts.factories import CartFactory
from apps.catalog.factories import ProductVariantFactory

from .models import Address, Order, OrderItem


class AddressFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = Address

    full_name = "Mali Example"
    phone = "0812345678"
    address_line_1 = "99 Fictional Coffee Lane"
    address_line_2 = "Unit 4B"
    subdistrict = "Khlong Tan Nuea"
    district = "Watthana"
    province = "Bangkok"
    postal_code = "10110"
    country_code = "TH"


class OrderFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = Order

    cart = factory.SubFactory(CartFactory)
    shipping_address = factory.SubFactory(AddressFactory)
    idempotency_key_hash = factory.Sequence(
        lambda number: hashlib.sha256(f"order-key-{number}".encode()).hexdigest()
    )
    request_fingerprint = factory.Sequence(
        lambda number: hashlib.sha256(f"request-{number}".encode()).hexdigest()
    )
    customer_email = factory.Sequence(lambda number: f"customer-{number}@example.test")
    shipping_method = "standard_th"
    shipping_method_name = "Standard delivery"
    subtotal = Decimal("850.00")
    discount_total = Decimal("0.00")
    shipping_total = Decimal("0.00")
    tax_total = Decimal("0.00")
    total = Decimal("850.00")


class OrderItemFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    product_name = "Fictional Coffee"
    sku = factory.Sequence(lambda number: f"ORDER-SKU-{number}")
    option_name = "250 g, whole bean"
    weight_grams = 250
    grind = "whole_bean"
    unit_price = Decimal("850.00")
    quantity = 1
    line_subtotal = Decimal("850.00")
    discount_total = Decimal("0.00")
    tax_total = Decimal("0.00")
    line_total = Decimal("850.00")
