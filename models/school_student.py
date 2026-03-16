from odoo import fields, models


class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "School Student"
    _order = "name"

    name = fields.Char(string="Student Name", required=True)
    code = fields.Char(string="Student Code", required=True)
    user_id = fields.Many2one("res.users", string="User")
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    admission_date = fields.Date(string="Admission Date")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    address = fields.Text(string="Address")
    image = fields.Image(string="Photo")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("student_code_unique", "unique(code)", "Student code must be unique."),
    ]