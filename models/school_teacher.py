from odoo import fields, models, api
from odoo.exceptions import ValidationError


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

    @api.constrains('user_id')
    def _check_duplicate_user(self):
        for rec in self:
            if not rec.user_id:
                continue

            domain = [
                ('id', '!=', rec.id),
                ('user_id', '=', rec.user_id.id),
            ]

            if self.search_count(domain):
                raise ValidationError(
                    "This user is already assigned to another teacher."
                )

    @api.onchange('user_id')
    def _onchange_user_id(self):
        for rec in self:
            if not rec.user_id:
                continue

            rec.name = rec.user_id.name or ""
            rec.email = rec.user_id.email or ""

            if hasattr(rec.user_id, 'phone'):
                rec.phone = rec.user_id.phone or ""

            rec.image = rec.user_id.image_1920