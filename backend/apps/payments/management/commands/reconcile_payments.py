from collections import Counter
from typing import Any

from django.core.management.base import BaseCommand

from apps.payments.models import PaymentAttempt
from apps.payments.providers import get_payment_provider
from apps.payments.services import reconcile_payment_attempt


class Command(BaseCommand):
    help = "Reconcile recent Stripe Checkout Sessions with BeanCo payment and order state."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args: object, **options: Any) -> None:
        limit = max(1, min(int(options["limit"]), 1000))
        attempts = PaymentAttempt.objects.exclude(
            provider_checkout_session_id__isnull=True
        ).exclude(provider_checkout_session_id="")[:limit]
        provider = get_payment_provider()
        outcomes: Counter[str] = Counter()
        for attempt in attempts:
            try:
                outcomes[reconcile_payment_attempt(attempt=attempt, provider=provider)] += 1
            except Exception:
                outcomes["provider_or_processing_error"] += 1
        summary = ", ".join(f"{name}={count}" for name, count in sorted(outcomes.items()))
        self.stdout.write(self.style.SUCCESS(summary or "No payment attempts to reconcile."))
