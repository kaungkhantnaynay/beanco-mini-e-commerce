from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalog.models import ProductVariant

from .models import InventoryRecord, InventoryTransaction


@transaction.atomic
def adjust_inventory(
    *,
    variant: ProductVariant,
    quantity_change: int = 0,
    reserved_change: int = 0,
    reason: str,
    reference: str = "",
    actor: object | None = None,
) -> InventoryRecord:
    if quantity_change == 0 and reserved_change == 0:
        raise ValidationError("An inventory adjustment must change a quantity.")

    record = InventoryRecord.objects.select_for_update().get(variant=variant)
    new_available = record.available_quantity + quantity_change
    new_reserved = record.reserved_quantity + reserved_change
    if new_available < 0 or new_reserved < 0 or new_reserved > new_available:
        raise ValidationError("The inventory adjustment would create invalid quantities.")

    record.available_quantity = new_available
    record.reserved_quantity = new_reserved
    record.save(update_fields=("available_quantity", "reserved_quantity", "updated_at"))
    user_model = get_user_model()
    valid_actor = actor if isinstance(actor, user_model) else None
    InventoryTransaction.objects.create(
        variant=variant,
        quantity_change=quantity_change,
        reserved_change=reserved_change,
        reason=reason,
        reference=reference,
        actor=valid_actor,
    )
    return record
