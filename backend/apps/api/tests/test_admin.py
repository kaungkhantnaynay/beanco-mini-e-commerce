from typing import cast

import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.accounts.factories import UserFactory
from apps.accounts.models import User
from apps.catalog.models import Category, Product, ProductImage, ProductVariant
from apps.communications.models import NewsletterSubscription, PartnershipInquiry
from apps.inventory.admin import InventoryRecordAdmin, InventoryTransactionAdmin
from apps.inventory.factories import InventoryRecordFactory, InventoryTransactionFactory
from apps.inventory.models import InventoryRecord, InventoryTransaction


def test_all_phase_two_models_are_registered_in_admin() -> None:
    expected_models = {
        Category,
        Product,
        ProductVariant,
        ProductImage,
        InventoryRecord,
        InventoryTransaction,
        PartnershipInquiry,
        NewsletterSubscription,
    }

    assert expected_models.issubset(admin.site._registry)


@pytest.mark.django_db
def test_admin_inventory_edit_creates_audit_transaction() -> None:
    record = cast(InventoryRecord, InventoryRecordFactory(available_quantity=10))
    staff = cast(User, UserFactory(is_staff=True))
    request = RequestFactory().post("/admin/inventory/inventoryrecord/")
    request.user = staff
    record.available_quantity = 12
    model_admin = InventoryRecordAdmin(InventoryRecord, admin.site)

    model_admin.save_model(request, record, form=None, change=True)

    transaction = InventoryTransaction.objects.get(variant=record.variant)
    assert transaction.quantity_change == 2
    assert transaction.actor == staff


@pytest.mark.django_db
def test_inventory_transaction_admin_is_read_only() -> None:
    transaction = cast(InventoryTransaction, InventoryTransactionFactory())
    model_admin = InventoryTransactionAdmin(InventoryTransaction, admin.site)
    request = RequestFactory().get("/admin/inventory/inventorytransaction/")

    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request, transaction)
    assert not model_admin.has_delete_permission(request, transaction)
