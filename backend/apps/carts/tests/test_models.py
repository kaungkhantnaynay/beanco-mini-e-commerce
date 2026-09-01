from typing import cast

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.carts.factories import CartItemFactory
from apps.carts.models import CartItem


@pytest.mark.django_db
@pytest.mark.parametrize("quantity", [0, 100])
def test_cart_item_quantity_validation(quantity: int) -> None:
    item = CartItemFactory.build(quantity=quantity)

    with pytest.raises(ValidationError):
        item.full_clean()

    valid_item = cast(CartItem, CartItemFactory())
    with pytest.raises(IntegrityError), transaction.atomic():
        CartItem.objects.filter(pk=valid_item.pk).update(quantity=quantity)


@pytest.mark.django_db
def test_cart_database_prevents_duplicate_variant() -> None:
    first = cast(CartItem, CartItemFactory())

    with pytest.raises(IntegrityError), transaction.atomic():
        CartItem.objects.create(cart=first.cart, variant=first.variant, quantity=1)
