from typing import Any, cast

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.carts.serializers import ShippingAddressSerializer

from .models import SavedAddress, User


class StrictInputSerializer(serializers.Serializer[Any]):
    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed."] for field in sorted(unknown)}
                )
        return cast(dict[str, Any], super().to_internal_value(data))


class RegistrationSerializer(StrictInputSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        return User.objects.normalize_email(value).strip().lower()

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        candidate = User(
            email=str(attrs["email"]),
            first_name=str(attrs.get("first_name", "")),
            last_name=str(attrs.get("last_name", "")),
        )
        try:
            validate_password(str(attrs["password"]), candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class LoginSerializer(StrictInputSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate_email(self, value: str) -> str:
        return User.objects.normalize_email(value).strip().lower()


class EmailTokenSerializer(StrictInputSerializer):
    uid = serializers.CharField(max_length=32)
    token = serializers.CharField(max_length=128, write_only=True)


class PasswordResetRequestSerializer(StrictInputSerializer):
    email = serializers.EmailField(max_length=254)

    def validate_email(self, value: str) -> str:
        return User.objects.normalize_email(value).strip().lower()


class PasswordResetConfirmSerializer(EmailTokenSerializer):
    new_password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value


class AccountSerializer(serializers.ModelSerializer[User]):
    email_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "email_verified")
        read_only_fields = fields

    def get_email_verified(self, obj: User) -> bool:
        return obj.email_verified_at is not None


class ProfileUpdateSerializer(StrictInputSerializer):
    first_name = serializers.CharField(max_length=150, allow_blank=True)
    last_name = serializers.CharField(max_length=150, allow_blank=True)


class SavedAddressSerializer(ShippingAddressSerializer):
    public_id = serializers.UUIDField(read_only=True)
    label = serializers.CharField(min_length=1, max_length=40)  # type: ignore[assignment]
    is_default = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data: dict[str, Any]) -> SavedAddress:
        return SavedAddress.objects.create(**validated_data)

    def update(self, instance: SavedAddress, validated_data: dict[str, Any]) -> SavedAddress:
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class DetailSerializer(serializers.Serializer[dict[str, str]]):
    detail = serializers.CharField()
