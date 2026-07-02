from odoo import fields, models, api
from odoo.exceptions import ValidationError

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
        
    
    def action_confirm(self):
        for rec in self:

            if rec.state != "draft":
                continue

            if rec.amount <= 0:
                raise ValidationError(
                    "Payment amount must be greater than zero."
                )

            rec.fee_line_id.paid_amount += rec.amount

            rec.state = "paid"


    def action_cancel(self):
        for rec in self:

            if rec.state != "draft":
                continue

            rec.state = "cancel"