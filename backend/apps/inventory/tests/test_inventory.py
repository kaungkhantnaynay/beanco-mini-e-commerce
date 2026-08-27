from typing import cast

import pytest
from django.core.exceptions import ValidationError

from apps.inventory.factories import InventoryRecordFactory, InventoryTransactionFactory
from apps.inventory.models import InventoryRecord, InventoryTransaction
from apps.inventory.services import adjust_inventory


@pytest.mark.django_db
def test_inventory_adjustment_is_atomic_and_audited() -> None:
    record = cast(InventoryRecord, InventoryRecordFactory(available_quantity=10))

    adjusted = adjust_inventory(
        variant=record.variant,
        quantity_change=5,
        reason=InventoryTransaction.Reason.RECEIPT,
        reference="Fictional delivery",
    )

    assert adjusted.available_quantity == 15
    transaction = InventoryTransaction.objects.get(variant=record.variant)
    assert transaction.quantity_change == 5
    assert transaction.reference == "Fictional delivery"


@pytest.mark.django_db
def test_invalid_inventory_adjustment_rolls_back() -> None:
    record = cast(InventoryRecord, InventoryRecordFactory(available_quantity=2))

    with pytest.raises(ValidationError):
        adjust_inventory(
            variant=record.variant,
            quantity_change=-3,
            reason=InventoryTransaction.Reason.ADJUSTMENT,
        )

    record.refresh_from_db()
    assert record.available_quantity == 2
    assert not InventoryTransaction.objects.filter(variant=record.variant).exists()


@pytest.mark.django_db
def test_inventory_transactions_cannot_be_changed_or_deleted() -> None:
    inventory_transaction = cast(InventoryTransaction, InventoryTransactionFactory())
    inventory_transaction.reference = "Changed"

    with pytest.raises(ValidationError):
        inventory_transaction.save()
    with pytest.raises(ValidationError):
        inventory_transaction.delete()
