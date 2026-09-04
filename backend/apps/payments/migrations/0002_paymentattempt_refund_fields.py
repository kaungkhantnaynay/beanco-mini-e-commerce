from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="paymentattempt",
            name="provider_refund_id",
            field=models.CharField(blank=True, editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name="paymentattempt",
            name="refunded_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
