import hashlib
from datetime import timedelta

import factory
from django.utils import timezone

from apps.catalog.factories import ProductVariantFactory

from .models import Cart, CartItem


class CartFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = Cart

    token_hash = factory.Sequence(
        lambda number: hashlib.sha256(f"test-cart-{number}".encode()).hexdigest()
    )
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))


class CartItemFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    quantity = 1
