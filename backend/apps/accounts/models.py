import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q


class UserManager(BaseUserManager["User"]):
    """Create users with normalized email addresses."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("The email address must be set.")
        normalized_email = self.normalize_email(email).strip().lower()
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # type: ignore[assignment]
    email = models.EmailField("email address", unique=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()  # type: ignore[misc, assignment]

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email).strip().lower()


class SavedAddress(models.Model):
    """A reusable customer address; order addresses remain immutable snapshots."""

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_addresses")
    label = models.CharField(max_length=40)
    is_default = models.BooleanField(default=False)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(
        max_length=24,
        validators=[RegexValidator(r"^(?:\+66|0)\d{8,9}$", "Enter a valid Thai phone number.")],
    )
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    subdistrict = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=5,
        validators=[RegexValidator(r"^\d{5}$", "Enter a five-digit postal code.")],
    )
    country_code = models.CharField(max_length=2, default="TH")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_default", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=Q(is_default=True),
                name="accounts_one_default_address_per_user",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.email}: {self.label}"
