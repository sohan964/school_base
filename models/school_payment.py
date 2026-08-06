from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from ..services.bkash_api import BkashAPI

class SchoolPaymentMethod(models.Model):
    _name = "school.payment.method"
    _description = "School Payment Method"


    name = fields.Char(
        required=True
    )

    code = fields.Char(
        required=True
    )


    active = fields.Boolean(
        default=True
    )

    notes = fields.Text()

    _unique_payment_method = models.Constraint(
        "UNIQUE(code)",
        "Payment method code must be unique."
    )




class SchoolFeePayment(models.Model):
    _name = "school.fee.payment"
    _description = "Student Fee Payment"
    _order = "payment_date desc, id desc"

    name = fields.Char(
        readonly=True,
        copy=False,
        default="New"
    )

    fee_line_id = fields.Many2one(
        "school.fee.batch.line",
        string="Fee",
        required=True,
        ondelete="cascade"
    )

    student_id = fields.Many2one(
        "school.student",
        related="fee_line_id.student_id",
        store=True,
        readonly=True
    )

    due_amount = fields.Monetary(
        related="fee_line_id.due_amount",
        store=True,
        readonly=True
    )

    payment_date = fields.Date(
        default=fields.Date.context_today,
        required=True
    )

    payment_method_id = fields.Many2one(
        "school.payment.method",
        required=True
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    amount = fields.Monetary(
        currency_field="currency_id",
        required=True
    )

    reference = fields.Char()

    transaction_id = fields.Char()

    remarks = fields.Text()

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("paid", "Paid"),
            ("cancel", "Cancelled"),
        ],
        default="draft"
    )

    @api.onchange("fee_line_id")
    def _onchange_fee_line_id(self):
        for rec in self:
            if rec.fee_line_id:
                rec.amount = rec.fee_line_id.due_amount
            else:
                rec.amount = 0.0

    @api.onchange("amount")
    def _onchange_amount(self):
        if (
            self.fee_line_id
            and self.amount > self.fee_line_id.due_amount
        ):
            self.amount = self.fee_line_id.due_amount

            return {
                "warning": {
                    "title": "Invalid Amount",
                    "message": "Payment amount cannot be greater than the due amount.",
                }
            }
    
    @api.constrains("amount", "fee_line_id")
    def _check_payment_amount(self):
        for rec in self:
            if rec.fee_line_id and rec.amount > rec.fee_line_id.due_amount:
                raise ValidationError(
                    "Payment amount cannot be greater than the due amount."
                )
            
    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "school.fee.payment"
                ) or "New"

        return super().create(vals_list)
            
    def write(self, vals):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(
                    "Only draft payments can be modified."
                )

        return super().write(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(
                    "Only draft payments can be deleted."
                )
        return super().unlink()
        
    
    def action_confirm(self):
        for rec in self:

            if rec.state != "draft":
                continue

            if rec.amount <= 0:
                raise ValidationError(
                    "Payment amount must be greater than zero."
                )
            rec.state = "paid"


    def action_cancel(self):
        for rec in self:

            if rec.state != "draft":
                continue
            rec.state = "cancel"



    # this are about payment by student dashboard
    
    @api.model
    def student_pay_fee(self, values):
        """
        Entry point for student online payment.
        """

        fee_line_id = values.get("fee_line_id")
        payment_method_id = values.get("payment_method_id")
        amount = values.get("amount")

        fee_line = self.env["school.fee.batch.line"].browse(
            fee_line_id
        )

        if not fee_line.exists():
            raise ValidationError(
                _("Fee line not found.")
            )

        if amount <= 0:
            raise ValidationError(
                _("Amount must be greater than zero.")
            )

        if amount > fee_line.due_amount:
            raise ValidationError(
                _("Amount cannot be greater than due amount.")
            )

        payment_method = self.env[
            "school.payment.method"
        ].browse(payment_method_id)

        payment = self.create({
            "fee_line_id": fee_line.id,
            "payment_method_id": payment_method.id,
            "amount": amount,
        })

        if payment_method.code == "bkash":
            return payment._start_bkash_payment()

        return {
            "success": True,
            "payment_id": payment.id,
            "message": "Payment created successfully.",
        }


    def _start_bkash_payment(self):
        self.ensure_one()

        api = BkashAPI(self.env)

        callback_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url")
            + "/bkash/callback"
        )

        merchant_invoice = self.name

        result = api.create_payment(
            amount=self.amount,
            payer_reference="",
            merchant_invoice=merchant_invoice,
            callback_url=callback_url,
        )

        if result.get("statusCode") != "0000":
            raise ValidationError(
                result.get("statusMessage")
            )

        bkash_payment = self.env[
            "school.bkash.payment"
        ].create({
            "fee_payment_id": self.id,
            "amount": self.amount,
            "payer_reference": self.student_id.phone or "",
            "merchant_invoice": merchant_invoice,
            "callback_url": callback_url,
            "bkash_payment_id": result.get("paymentID"),
            "bkash_url": result.get("bkashURL"),
            "status": "pending",
            "create_response": str(result),
        })

        return {
            "success": True,
            "redirect_url": bkash_payment.bkash_url,
        }