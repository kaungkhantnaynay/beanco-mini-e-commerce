from decimal import Decimal
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Category, Product, ProductImage, ProductVariant
from apps.inventory.models import InventoryRecord, InventoryTransaction

PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "slug": "ethiopian-yirgacheffe",
        "name": "Ethiopian Yirgacheffe",
        "price": "850.00",
        "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&q=80&w=1000",
        "description": (
            "Bright and floral with notes of jasmine and lemon. A classic Ethiopian coffee."
        ),
        "profile": "Floral, citrus, honey",
        "category": "coffee",
        "type": Product.ProductType.COFFEE,
    },
    {
        "slug": "colombian-supremo",
        "name": "Colombian Supremo",
        "price": "650.00",
        "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&q=80&w=1000",
        "description": "Balanced and smooth with caramel sweetness and nutty undertones.",
        "profile": "Caramel, almond, cocoa",
        "category": "coffee",
        "type": Product.ProductType.COFFEE,
    },
    {
        "slug": "sumatra-mandheling",
        "name": "Sumatra Mandheling",
        "price": "780.00",
        "image": "sumatra-mandheling.png",
        "description": "Full-bodied and earthy with a rich, complex flavor profile.",
        "profile": "Earthy, spice, dark chocolate",
        "category": "coffee",
        "type": Product.ProductType.COFFEE,
    },
    {
        "slug": "espresso-blend",
        "name": "Espresso Blend",
        "price": "700.00",
        "image": "espresso-blend.png",
        "description": "A bold and intense blend perfect for espresso shots and milk-based drinks.",
        "profile": "Molasses, toasted nut, crema",
        "category": "coffee",
        "type": Product.ProductType.COFFEE,
    },
    {
        "slug": "ceramic-coffee-cup",
        "name": "Ceramic Coffee Cup",
        "price": "420.00",
        "image": "ceramic-cup.png",
        "description": "Minimalist ceramic cup with a matte finish, perfect for your daily brew.",
        "profile": "Cafe-grade ceramic",
        "category": "drinkware",
        "type": Product.ProductType.DRINKWARE,
    },
    {
        "slug": "pour-over-kit",
        "name": "Pour Over Kit",
        "price": "1550.00",
        "image": "pour-over-kit.png",
        "description": "Complete pour over kit including a glass carafe, dripper, and kettle.",
        "profile": "Precision brewing kit",
        "category": "equipment",
        "type": Product.ProductType.EQUIPMENT,
    },
    {
        "slug": "coffee-grinder",
        "name": "Coffee Grinder",
        "price": "2990.00",
        "image": "coffee-grinder.png",
        "description": "Premium electric grinder for consistent and precise coffee grounds.",
        "profile": "Consistent cafe grind",
        "category": "equipment",
        "type": Product.ProductType.EQUIPMENT,
    },
    {
        "slug": "travel-mug",
        "name": "Travel Mug",
        "price": "850.00",
        "image": "travel-mug.png",
        "description": "Insulated stainless steel travel mug to keep your coffee hot on the go.",
        "profile": "Insulated stainless steel",
        "category": "drinkware",
        "type": Product.ProductType.DRINKWARE,
    },
)

CATEGORIES = {
    "coffee": ("Coffee", "Single-origin coffees and signature blends.", 0),
    "equipment": ("Equipment", "Tools for consistent coffee brewing.", 1),
    "drinkware": ("Drinkware", "Cups and travel drinkware.", 2),
}


class Command(BaseCommand):
    help = "Idempotently import the eight original storefront products."

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        categories = {
            slug: Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": values[0],
                    "description": values[1],
                    "display_order": values[2],
                    "is_active": True,
                },
            )[0]
            for slug, values in CATEGORIES.items()
        }

        for position, data in enumerate(PRODUCTS):
            product, _ = Product.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "category": categories[data["category"]],
                    "name": data["name"],
                    "product_type": data["type"],
                    "description": data["description"],
                    "profile": data["profile"],
                    "is_featured": position < 4,
                    "is_active": True,
                    "seo_title": data["name"],
                    "seo_description": data["description"][:160],
                },
            )
            is_coffee = data["type"] == Product.ProductType.COFFEE
            variant, _ = ProductVariant.objects.update_or_create(
                sku=f"BEANCO-{position + 1:03d}",
                defaults={
                    "product": product,
                    "option_name": "250 g · Whole bean" if is_coffee else "Standard",
                    "weight_grams": 250 if is_coffee else None,
                    "grind": ProductVariant.Grind.WHOLE_BEAN if is_coffee else "",
                    "price": Decimal(data["price"]),
                    "is_active": True,
                },
            )
            inventory, created = InventoryRecord.objects.get_or_create(
                variant=variant,
                defaults={"available_quantity": 20, "reserved_quantity": 0},
            )
            if created:
                InventoryTransaction.objects.create(
                    variant=variant,
                    quantity_change=inventory.available_quantity,
                    reason=InventoryTransaction.Reason.INITIAL,
                    reference="Original storefront catalog import",
                )
            self._upsert_image(product, str(data["image"]))

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} BeanCo products."))

    def _upsert_image(self, product: Product, source: str) -> None:
        product_image = ProductImage.objects.filter(product=product, display_order=0).first()
        if product_image is None:
            product_image = ProductImage(product=product, display_order=0, alt_text=product.name)
        product_image.alt_text = product.name
        if source.startswith("https://"):
            product_image.external_url = source
            if product_image.image:
                product_image.image.delete(save=False)
            product_image.image = ""
        else:
            source_path = Path(settings.BASE_DIR).parent / "public" / "images" / source
            if not source_path.exists():
                raise FileNotFoundError(f"Seed image does not exist: {source_path}")
            product_image.external_url = ""
            if not product_image.image or Path(product_image.image.name).name != source:
                with source_path.open("rb") as image_file:
                    product_image.image.save(source, File(image_file), save=False)
        product_image.full_clean()
        product_image.save()
