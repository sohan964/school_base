from odoo import fields, models


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "School Teacher"
    _order = "name"

    name = fields.Char(string="Teacher Name", required=True)
    code = fields.Char(string="Code", required=True)
    user_id = fields.Many2one("res.users", string="user")
    department_id = fields.Many2one(
        "school.department",
        string="Department",
        required=True,
        ondelete="restrict",
    )
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    date_of_birth = fields.Date(string="Date of Birth")
    joining_date = fields.Date(string="Joining Date")
    designation = fields.Char(string="Designation")
    address = fields.Text(string="Address")
    image = fields.Image(string="Image")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Employee code must be unique."),
    ]