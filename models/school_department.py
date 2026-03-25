from odoo import api, fields, models


class SchoolDepartment(models.Model):
    _name="school.department"
    _description = "All departments of School"
    _order = "name"

    name = fields.Char(string="Department Name", required=True)
    code = fields.Char(string="Department Code", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    logo = fields.Image()
    _sql_constraints = [
        ("code_unique", "unique(code)", "Department code must be unique."),
        ("name_unique", "unique(name)", "Department name must be unique."),
    ]
    