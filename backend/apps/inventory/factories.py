import factory

from apps.catalog.factories import ProductVariantFactory

from .models import InventoryRecord, InventoryTransaction


class InventoryRecordFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = InventoryRecord

    variant = factory.SubFactory(ProductVariantFactory)
    available_quantity = 20
    reserved_quantity = 0


class InventoryTransactionFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = InventoryTransaction

    variant = factory.SubFactory(ProductVariantFactory)
    quantity_change = 10
    reason = InventoryTransaction.Reason.RECEIPT
