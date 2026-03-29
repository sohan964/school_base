from odoo import api, fields, models
from odoo.exceptions import ValidationError

#create attendance for that class
class SchoolStudentAttendance(models.Model):
    _name = "school.student.attendance"
    _description = "Student Attendance Per Class"

    teacher_id = fields.Many2one(
        "school.teacher",
        string="Teacher",
        # default=lambda self: self.env['school.teacher'].search([('user_id', '=', self.env.uid)], limit=1)
    )
    year_id = fields.Many2one("school.academic.year", string="Year")
    
    day_id = fields.Many2one("school.weekly.day", string="Day")
    slot_id = fields.Many2one("school.time.slot", string="Slot")
    date = fields.Date(string="Date", required = True)
    teacher_assignment_id = fields.Many2one("school.teacher.assignment", 
                                            domain="[('teacher_id', '=', teacher_id),('year_id', '=', year_id), ('day_id','=',day_id),('slot_id','=', slot_id)]",
                                              string="Routine")
    attendance_line_ids = fields.One2many(
        "school.student.attendance.line",
        "attendance_id",
        string="Students"
    )

    @api.constrains('date', 'teacher_assignment_id')
    def _check_duplicate_attendance(self):
        for rec in self:
            domain=[
                ('id', '!=', rec.id),
                ('date', '=', rec.date),
                ('teacher_assignment_id', '=', rec.teacher_assignment_id)
            ]
        if self.search_count(domain):
            raise ValidationError("Attedance already taken")


    
    # this is about about to load student
    @api.onchange('teacher_assignment_id')
    def _onchange_teacher_assignment(self):
        for rec in self:
            rec.attendance_line_ids = [(5, 0, 0)]
            

            if not rec.teacher_assignment_id:
                continue

            assignment = rec.teacher_assignment_id

            enrollments = self.env['school.student.enrollment'].search([
                ('class_id', '=', assignment.class_id.id),
                ('section_id', '=', assignment.section_id.id),
                ('year_id', '=', assignment.year_id.id),
                ('state', '=', 'active'),
            ])

            # print("enrollment>>>>>>>>>>>>>>>>>>>>>>>>",enrollments)

            lines = []
            for enroll in enrollments:
                # print("enroll>>>>>>>>>>>", enroll)
                lines.append((0, 0, {
                    'enrollment_id': enroll.id,
                    'status': 'present',
                }))

            rec.attendance_line_ids = lines

    
#take attendance of each students
class SchoolStudentAttendanceLine(models.Model):
    _name = "school.student.attendance.line"
    _description = "take attendance per students"

    attendance_id = fields.Many2one(
        "school.student.attendance",
        string="Attendance",
        ondelete="cascade"
    )

    enrollment_id = fields.Many2one(
        "school.student.enrollment",
        # string="Student",
        required=True
    )

    student_id = fields.Many2one(
        "school.student",
        related="enrollment_id.student_id",
        string="Student",
        store=True
    )

    status = fields.Selection([
        ('present', "Present"),
        ('absent', "Absent"),
        ('late', "Late")
    ], default='present')

    

    # department_id = fields.Many2one("school.department",  string="Department")
    # class_id = fields.Many2one("school.class", string="Class")
    # section_id = fields.Many2one("school.class.section", string="Section", domain="[('department_id', '=', department_id), ('class_id','=', class_id)]")
    # subject_id = fields.Many2one("school.class.subject", string="Subject", 
    #                              domain="[('department_ids', '=', department_id), ('class_ids','=', class_id)]")