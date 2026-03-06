import stripe
from src.config import settings


def _get_stripe():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def create_product_checkout_url(
    items: list[dict], customer_email: str | None = None
) -> str:
    s = _get_stripe()
    line_items = []
    for item in items:
        line_items.append(
            {
                "price_data": {
                    "currency": "cad",
                    "product_data": {"name": item["name"]},
                    "unit_amount": int(item["price"] * 100),
                },
                "quantity": item.get("quantity", 1),
            }
        )

    session = s.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=f"{settings.FRONTEND_URL}/merci?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/boutique",
        customer_email=customer_email,
    )
    return session.url


def create_booking_checkout_url(
    service_name: str,
    price: float,
    date_str: str,
    customer_email: str | None = None,
) -> str:
    s = _get_stripe()
    session = s.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "cad",
                    "product_data": {
                        "name": f"Reservation: {service_name}",
                        "description": f"Date: {date_str} - Mwema Beauty Salon",
                    },
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{settings.FRONTEND_URL}/reservation-confirmee?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/salon",
        customer_email=customer_email,
    )
    return session.url
