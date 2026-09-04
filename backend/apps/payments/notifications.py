from django.conf import settings
from django.core.mail import get_connection, send_mail

from apps.orders.models import Order


def _send(*, subject: str, body: str, recipient: str) -> None:
    connection = get_connection(backend=settings.PAYMENT_EMAIL_BACKEND)
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        connection=connection,
    )


def send_order_confirmation(order: Order) -> None:
    _send(
        subject=f"BeanCo order {order.public_id} confirmed",
        body=(
            f"Your payment was received and order {order.public_id} is confirmed.\n"
            f"Total: {order.total} {order.currency}."
        ),
        recipient=order.customer_email,
    )


def send_payment_failure(order: Order) -> None:
    _send(
        subject=f"BeanCo payment unsuccessful for order {order.public_id}",
        body=(
            f"Payment for order {order.public_id} was not completed. "
            "The order was cancelled and reserved stock was released."
        ),
        recipient=order.customer_email,
    )


def send_refund_confirmation(order: Order) -> None:
    _send(
        subject=f"BeanCo refund issued for order {order.public_id}",
        body=(
            f"A refund of {order.total} {order.currency} was issued for order "
            f"{order.public_id}. Your bank may take several days to display it."
        ),
        recipient=order.customer_email,
    )
