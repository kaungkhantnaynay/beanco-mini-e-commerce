import pytest
from django.core.management import call_command

from apps.catalog.models import Category, Product, ProductImage, ProductVariant
from apps.inventory.models import InventoryRecord, InventoryTransaction


@pytest.mark.django_db
def test_seed_catalog_imports_eight_products_without_duplication(
    tmp_path: object, settings: object
) -> None:
    settings.MEDIA_ROOT = tmp_path  # type: ignore[attr-defined]

    call_command("seed_catalog")
    call_command("seed_catalog")

    assert Category.objects.count() == 3
    assert Product.objects.count() == 8
    assert ProductVariant.objects.count() == 8
    assert ProductImage.objects.count() == 8
    assert InventoryRecord.objects.count() == 8
    assert InventoryTransaction.objects.count() == 8
    assert Product.objects.get(slug="ethiopian-yirgacheffe").variants.get().price == 850
