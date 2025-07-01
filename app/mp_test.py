import mercadopago
from flask import Blueprint, render_template
import os

mercadopago_routes = Blueprint('mercadopago_routes', __name__)

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

@mercadopago_routes.route("/checkout")
def checkout():
    preference_data = {
        "items": [
            {
                "title": "Mi producto",
                "quantity": 1,
                "unit_price": 75.76,
            }
        ],
        "back_urls": {
            "success": "https://www.tu-sitio.com/success",
            "failure": "https://www.tu-sitio.com/failure",
            "pending": "https://www.tu-sitio.com/pending"
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return render_template(
        "checkout.html",
        preference_id=preference["id"],
        public_key=os.getenv("MP_PUBLIC_KEY", "MP_PUBLIC_KEY")
    )

