from odoo import http
from odoo.http import request

from ..services.bkash_api import BkashAPI

class BkashController(http.Controller):

    @http.route(
        "/bkash/callback",
        type="http",
        auth="public",
        csrf=False,
    )
    def callback(self, **kwargs):

        payment_id = kwargs.get("paymentID")
        status = kwargs.get("status")

        payment = request.env["school.bkash.payment"].sudo().search(
            [("payment_id", "=", payment_id)],
            limit=1,
        )

        if not payment:
            return "Payment not found."

        if status == "success":

            api = BkashAPI(request.env)

            result = api.execute_payment(payment_id)

            payment.write({
                "trx_id": result.get("trxID"),
                "status": "paid",
            })

            return "Payment Successful"

        elif status == "failure":

            payment.write({
                "status": "failed",
            })

            return "Payment Failed"

        elif status == "cancel":

            payment.write({
                "status": "draft",
            })

            return "Payment Cancelled"

        return "Unknown Status"