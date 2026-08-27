from decimal import Decimal, InvalidOperation

from django.db.models import Exists, F, Min, OuterRef, Prefetch, Q, QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from apps.api.serializers import ApiErrorSerializer
from apps.inventory.models import InventoryRecord

from .models import Category, Product, ProductImage, ProductVariant
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet[Category]):
    serializer_class = CategorySerializer
    lookup_field = "slug"
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet[Category]:
        return Category.objects.filter(is_active=True).order_by("display_order", "name")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter("category", OpenApiTypes.STR, description="Category slug."),
            OpenApiParameter("type", OpenApiTypes.STR, enum=Product.ProductType.values),
            OpenApiParameter("featured", OpenApiTypes.BOOL),
            OpenApiParameter("availability", OpenApiTypes.BOOL),
            OpenApiParameter("search", OpenApiTypes.STR),
            OpenApiParameter("minimum_price", OpenApiTypes.DECIMAL),
            OpenApiParameter("maximum_price", OpenApiTypes.DECIMAL),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                enum=["name", "-name", "price", "-price"],
            ),
        ],
        responses={200: ProductListSerializer(many=True), 400: ApiErrorSerializer},
    )
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet[Product]):
    lookup_field = "slug"
    http_method_names = ["get", "head", "options"]

    def get_serializer_class(self) -> type[ProductListSerializer]:
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer

    def get_queryset(self) -> QuerySet[Product]:
        active_variant = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
        )
        active_inventory = InventoryRecord.objects.filter(
            variant__product=OuterRef("pk"),
            variant__is_active=True,
            available_quantity__gt=F("reserved_quantity"),
        )
        active_variants = ProductVariant.objects.filter(is_active=True).select_related("inventory")
        queryset = (
            Product.objects.filter(is_active=True, category__is_active=True)
            .select_related("category")
            .annotate(
                has_active_variant=Exists(active_variant),
                starting_price=Min("variants__price", filter=Q(variants__is_active=True)),
                available=Exists(active_inventory),
            )
            .filter(has_active_variant=True)
            .prefetch_related(
                Prefetch("variants", queryset=active_variants),
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(
                        Q(variant__isnull=True) | Q(variant__is_active=True)
                    ).select_related("variant"),
                ),
            )
        )
        return self._apply_filters(queryset)

    def _apply_filters(self, queryset: QuerySet[Product]) -> QuerySet[Product]:
        params = self.request.query_params
        if category := params.get("category"):
            queryset = queryset.filter(category__slug=category)
        if product_type := params.get("type"):
            valid_types = {choice for choice, _ in Product.ProductType.choices}
            if product_type not in valid_types:
                raise ValidationError({"type": ["Select a valid product type."]})
            queryset = queryset.filter(product_type=product_type)
        if featured := params.get("featured"):
            queryset = queryset.filter(is_featured=self._parse_boolean("featured", featured))
        if availability := params.get("availability"):
            queryset = queryset.filter(  # type: ignore[misc]
                available=self._parse_boolean("availability", availability)
            )
        if search := params.get("search"):
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(profile__icontains=search)
            )
        if minimum := params.get("minimum_price"):
            queryset = queryset.filter(  # type: ignore[misc]
                starting_price__gte=self._parse_decimal("minimum_price", minimum)
            )
        if maximum := params.get("maximum_price"):
            queryset = queryset.filter(  # type: ignore[misc]
                starting_price__lte=self._parse_decimal("maximum_price", maximum)
            )

        ordering = params.get("ordering", "name")
        ordering_fields = {
            "name": "name",
            "-name": "-name",
            "price": "starting_price",
            "-price": "-starting_price",
        }
        if ordering not in ordering_fields:
            raise ValidationError({"ordering": ["Order by name, -name, price, or -price."]})
        return queryset.order_by(ordering_fields[ordering], "pk")

    @staticmethod
    def _parse_boolean(field: str, value: str) -> bool:
        if value.lower() in {"true", "1"}:
            return True
        if value.lower() in {"false", "0"}:
            return False
        raise ValidationError({field: ["Enter true or false."]})

    @staticmethod
    def _parse_decimal(field: str, value: str) -> Decimal:
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ValidationError({field: ["Enter a valid decimal amount."]}) from exc
        if not parsed.is_finite() or parsed < 0:
            raise ValidationError({field: ["Enter a non-negative decimal amount."]})
        return parsed
