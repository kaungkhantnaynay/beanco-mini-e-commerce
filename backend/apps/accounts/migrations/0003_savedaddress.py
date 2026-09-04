import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_user_email_verified_at")]

    operations = [
        migrations.CreateModel(
            name="SavedAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("label", models.CharField(max_length=40)),
                ("is_default", models.BooleanField(default=False)),
                ("full_name", models.CharField(max_length=120)),
                (
                    "phone",
                    models.CharField(
                        max_length=24,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^(?:\\+66|0)\\d{8,9}$",
                                "Enter a valid Thai phone number.",
                            )
                        ],
                    ),
                ),
                ("address_line_1", models.CharField(max_length=200)),
                ("address_line_2", models.CharField(blank=True, max_length=200)),
                ("subdistrict", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("province", models.CharField(max_length=100)),
                (
                    "postal_code",
                    models.CharField(
                        max_length=5,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{5}$", "Enter a five-digit postal code."
                            )
                        ],
                    ),
                ),
                ("country_code", models.CharField(default="TH", max_length=2)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_addresses",
                        to="accounts.user",
                    ),
                ),
            ],
            options={"ordering": ("-is_default", "created_at")},
        ),
        migrations.AddConstraint(
            model_name="savedaddress",
            constraint=models.UniqueConstraint(
                condition=Q(is_default=True),
                fields=("user",),
                name="accounts_one_default_address_per_user",
            ),
        ),
    ]
