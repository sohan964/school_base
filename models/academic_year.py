from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class SchoolAcademicYear(models.Model):
    _name = "school.academic.year"
    _description = "Academic Year"
    _order = "date_start desc"

    name = fields.Char(required=True)
    code = fields.Char(required=True, readonly=True, default="New")
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("closed", "Closed"),
        ],
        default="draft",
        required=True,
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "Academic year code must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        current_year = datetime.now().year  # Get the current year (e.g., 2026)
        # Get the latest academic year code in the format Y_YYYY
        latest_code = self.search([('code', '=like', 'Y_%')], order='code desc', limit=1)
        for vals in vals_list:
            if not vals.get('code') or vals['code'] == "New":
                if latest_code:
                    # Get the last year from the latest code (Y_2026 -> 2026)
                    last_year = int(latest_code.code.split('_')[1])
                    # Set the new year code to be the next year
                    new_year = last_year + 1
                else:
                    # If no code exists yet, use the current year
                    new_year = current_year
                # Generate the code based on the current or new year
                vals["code"] = f"Y_{new_year}"
        return super().create(vals_list)
    
    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_end < rec.date_start:
                raise ValidationError("End date must be greater than start date.")