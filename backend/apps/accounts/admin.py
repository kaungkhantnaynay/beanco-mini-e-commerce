from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SavedAddress, User


@admin.register(User)
class BeanCoUserAdmin(UserAdmin):  # type: ignore[type-arg]
    model = User
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "email_verified_at",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("email_verified_at", "last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("label", "user", "province", "postal_code", "is_default", "updated_at")
    list_filter = ("is_default", "province")
    search_fields = ("user__email", "label", "full_name", "phone")
    readonly_fields = ("public_id", "created_at", "updated_at")
