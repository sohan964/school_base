from odoo import fields, models, api
from odoo.exceptions import ValidationError
# create new student
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

    @api.onchange('user_id')
    def _onchange_user_id(self):
        for rec in self:
            if not rec.user_id:
                continue

            rec.name = rec.user_id.name or ""
            rec.email = rec.user_id.email or ""

            # phone/mobile
            rec.phone = (
                rec.user_id.phone
                
                or ""
            )

            # user avatar
            rec.image = rec.user_id.image_1920

    _unique_student_user = models.Constraint(
        'UNIQUE(user_id)',
        'This user is already assigned to another student.'
    )

    _unique_student_code = models.Constraint(
        'UNIQUE(code)',
        'Student code must be unique.'
    )
    

# student enrollment to the class
class SchoolStudentEnrollment(models.Model):
    _name="school.student.enrollment"
    _description = "Student Enroll for class"

    student_id = fields.Many2one('school.student', string="Student", required=True)
    year_id = fields.Many2one("school.academic.year", string="Year", required=True)
    department_id = fields.Many2one("school.department", string="Department", required=True)
    class_id = fields.Many2one("school.class", string="Class", required=True)
    section_id = fields.Many2one("school.class.section", string="Section", 
                                 domain="[('department_id', '=', department_id), ('class_id', '=', class_id)]",
                                 required=True)
    roll_no = fields.Integer(string="Roll No")
    date_start = fields.Date(string="Started Date")
    date_end = fields.Date(string="End Date")
    state = fields.Selection([
        ("active", "Active"),
         ("completed","Completed"),
         ("droped","Droped")
    ],string="Status")

    @api.constrains('student_id', 'year_id', 'state')
    def _check_duplicate_enrollment(self):
        for rec in self:
            
            domain=[
                ('id', '!=', rec.id),
                ('student_id', '=', rec.student_id),
                ('year_id', '=', rec.year_id),
                ('state', '=', 'active')
            ]
            if self.search_count(domain):
                raise ValidationError("This student is already enrolled in this year with active status")
            
    

