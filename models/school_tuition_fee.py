from odoo import models, api, fields


class SchoolTuitionFee(models.Model):
    _name = "school.tuition.fee"
    _description = "Tuition Fee Setup"

    year_id = fields.Many2one(
        "school.academic.year",
        required=True
    )

    department_id = fields.Many2one(
        "school.department",
        required=True
    )

    class_id = fields.Many2one(
        "school.class",
        required=True
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    monthly_fee = fields.Monetary(
        currency_field="currency_id",
        string="Monthly Fee"
    )

    active = fields.Boolean(
        default=True
    )

    _check_unique_fee = models.Constraint(
        'UNIQUE(year_id, department_id, class_id)',
        'Fee configuration already exists.'
    )