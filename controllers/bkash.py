from odoo import http
from odoo.http import request
from markupsafe import escape

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

        # ---------------------------------------------------------
        # Validate callback parameters
        # ---------------------------------------------------------

        if not payment_id:
            return "Payment ID missing."

        if not status:
            return "Payment status missing."

        # ---------------------------------------------------------
        # Find bKash transaction
        # ---------------------------------------------------------

        payment = request.env[
            "school.bkash.payment"
        ].sudo().search(
            [
                ("bkash_payment_id", "=", payment_id),
            ],
            limit=1,
        )

        if not payment:
            return "bKash payment not found."

        # ---------------------------------------------------------
        # SUCCESS
        # ---------------------------------------------------------

        if status == "success":

            try:

                api = BkashAPI(request.env)

                result = api.execute_payment(payment_id)

                # Log execute response
                import logging
                _logger = logging.getLogger(__name__)

                _logger.info("=" * 80)
                _logger.info("bKash Execute Response: %s", result)
                _logger.info("=" * 80)

                # Check execute response
                if result.get("statusCode") != "0000":

                    payment.write({
                        "status": "failed",
                        "execute_response": str(result),
                    })

                    return (
                        "Payment execution failed: "
                        + result.get(
                            "statusMessage",
                            "Unknown error",
                        )
                    )

                # -------------------------------------------------
                # Payment successful
                # -------------------------------------------------

                payment.write({
                    "trx_id": result.get("trxID"),
                    "status": "paid",
                    "execute_response": str(result),
                })

                # -------------------------------------------------
                # Update School Fee Payment
                # -------------------------------------------------

                payment.fee_payment_id.write({
                    "state": "paid",
                    "transaction_id": result.get("trxID"),
                })

                return request.make_response(
                    f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Payment Successful</title>

                        <meta name="viewport"
                            content="width=device-width, initial-scale=1.0">

                        <style>

                            * {{
                                box-sizing: border-box;
                            }}

                            body {{
                                margin: 0;
                                padding: 0;
                                min-height: 100vh;

                                display: flex;
                                align-items: center;
                                justify-content: center;

                                background: #f5f7fb;

                                font-family:
                                    -apple-system,
                                    BlinkMacSystemFont,
                                    "Segoe UI",
                                    Roboto,
                                    Arial,
                                    sans-serif;
                            }}

                            .payment-card {{
                                width: 100%;
                                max-width: 520px;

                                background: #ffffff;

                                border-radius: 16px;

                                padding: 40px;

                                box-shadow:
                                    0 10px 40px rgba(0, 0, 0, 0.08);

                                text-align: center;
                            }}

                            .success-icon {{
                                width: 80px;
                                height: 80px;

                                margin: 0 auto 20px;

                                border-radius: 50%;

                                background: #e8f8ef;

                                display: flex;
                                align-items: center;
                                justify-content: center;

                                color: #198754;

                                font-size: 42px;
                                font-weight: bold;
                            }}

                            h1 {{
                                margin: 0 0 10px;

                                font-size: 28px;

                                color: #212529;
                            }}

                            .message {{
                                color: #6c757d;

                                margin-bottom: 30px;

                                font-size: 15px;
                            }}

                            .payment-info {{
                                background: #f8f9fa;

                                border-radius: 10px;

                                padding: 20px;

                                margin-bottom: 30px;

                                text-align: left;
                            }}

                            .info-row {{
                                display: flex;

                                justify-content: space-between;

                                gap: 20px;

                                padding: 10px 0;

                                border-bottom: 1px solid #e9ecef;
                            }}

                            .info-row:last-child {{
                                border-bottom: none;
                            }}

                            .label {{
                                color: #6c757d;
                            }}

                            .value {{
                                font-weight: 600;

                                color: #212529;

                                text-align: right;

                                word-break: break-word;
                            }}

                            .amount {{
                                color: #198754;

                                font-size: 18px;
                            }}

                            .dashboard-btn {{
                                display: inline-block;

                                width: 100%;

                                padding: 13px 20px;

                                border-radius: 8px;

                                background: #714B67;

                                color: white;

                                text-decoration: none;

                                font-weight: 600;

                                transition: 0.2s;
                            }}

                            .dashboard-btn:hover {{
                                background: #5f3f57;

                                color: white;
                            }}

                            .footer {{
                                margin-top: 20px;

                                font-size: 12px;

                                color: #adb5bd;
                            }}

                        </style>
                    </head>

                    <body>

                        <div class="payment-card">

                            <div class="success-icon">
                                ✓
                            </div>

                            <h1>
                                Payment Successful
                            </h1>

                            <div class="message">
                                Your tuition fee payment has been completed successfully.
                            </div>

                            <div class="payment-info">

                                <div class="info-row">
                                    <span class="label">
                                        Student
                                    </span>

                                    <span class="value">
                                        {escape(payment.fee_payment_id.student_id.name)}
                                    </span>
                                </div>

                                <div class="info-row">
                                    <span class="label">
                                        Amount Paid
                                    </span>

                                    <span class="value amount">
                                        ৳{escape(str(payment.amount))}
                                    </span>
                                </div>

                                <div class="info-row">
                                    <span class="label">
                                        Payment Reference
                                    </span>

                                    <span class="value">
                                        {escape(payment.fee_payment_id.name)}
                                    </span>
                                </div>

                                <div class="info-row">
                                    <span class="label">
                                        bKash Transaction ID
                                    </span>

                                    <span class="value">
                                        {escape(payment.trx_id or "-")}
                                    </span>
                                </div>

                            </div>

                            <a
                                href="/odoo/action-154"
                                class="dashboard-btn"
                            >
                                ← Back to Student Dashboard
                            </a>

                            <div class="footer">
                                Thank you for your payment.
                            </div>

                        </div>

                    </body>
                    </html>
                    """,
                    headers=[
                        ("Content-Type", "text/html; charset=utf-8")
                    ],
                )

            except Exception as e:

                import logging
                _logger = logging.getLogger(__name__)

                _logger.exception(
                    "Error while executing bKash payment"
                )

                payment.write({
                    "status": "failed",
                    "execute_response": str(e),
                })

                return "Payment processing failed."

        # ---------------------------------------------------------
        # FAILURE
        # ---------------------------------------------------------

        elif status == "failure":

            payment.write({
                "status": "failed",
                "execute_response": str(kwargs),
            })

            payment.fee_payment_id.write({
                "state": "cancel",
            })

            return "Payment Failed"

        # ---------------------------------------------------------
        # CANCEL
        # ---------------------------------------------------------

        elif status == "cancel":

            payment.write({
                "status": "failed",
                "execute_response": str(kwargs),
            })

            payment.fee_payment_id.write({
                "state": "cancel",
            })

            return "Payment Cancelled"

        return "Unknown Status"