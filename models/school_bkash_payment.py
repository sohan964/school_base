from odoo import api, fields, models


class SchoolBkashPayment(models.Model):
    _name = "school.bkash.payment"
    _description = "bKash Transactions"

    fee_payment_id = fields.Many2one(
        "school.fee.payment",
        required=True,
        ondelete="cascade",
    )

    bkash_payment_id = fields.Char(
        readonly=True,
    )

    create_response = fields.Text(
        string="Create Payment Response"
    )

    bkash_url = fields.Char(
        readonly=True,
    )

    trx_id = fields.Char(
        readonly=True,
    )

    amount = fields.Monetary(
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="fee_payment_id.currency_id",
        store=True,
    )

    payer_reference = fields.Char(
        string="Payer Reference",
        readonly=True,
    )

    merchant_invoice = fields.Char()

    callback_url = fields.Char()

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="draft",
    )


    execute_response = fields.Text()