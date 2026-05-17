from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolExamResult(models.Model):
    _name = "school.exam.result"
    _description = "All Exams result"

    teacher_id = fields.Many2one("school.teacher", string="Teacher",
        default=lambda self: self.env['school.teacher'].search([('user_id', '=', self.env.uid)], limit=1),
        readonly=True)
    year_id = fields.Many2one("school.academic.year", string="Year")
    department_id = fields.Many2one("school.department", string="Department")
    class_id = fields.Many2one("school.class", string="Class", domain="[('id', 'in', available_class_ids)]", required=True)
    
    section_id = fields.Many2one( "school.class.section", domain="[('id', 'in', available_section_ids), ('department_id', '=', department_id)]", string="Section")

    subject_id = fields.Many2one( "school.class.subject", domain="[('id', 'in', available_subject_ids), ('department_id', '=', department_id), ('class_id','=', class_id)]", string="Subject")
    exam_id = fields.Many2one("school.exam", string="Exam Name")
    exam_line_id = fields.Many2one(
        "school.exam.line",
        string="Exam line",
        domain = "[('department_id', '=', department_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('exam_id', '=', exam_id)]",
        required=True
    )

    result_ids = fields.One2many(
        "school.exam.result.line",
        "result_id",
        string="Result"
    )

    # these fields for get the class, section sujbect from teacher assignment (routine)
    available_class_ids = fields.Many2many(
        "school.class",
        compute="_compute_available_fields"
    )

    available_section_ids = fields.Many2many(
        "school.class.section",
        compute="_compute_available_fields"
    )

    available_subject_ids = fields.Many2many(
        "school.class.subject",
        compute="_compute_available_fields"
    )
    #these compute to filter class section, subjects form teacher assignment
    @api.depends('teacher_id', 'class_id')
    def _compute_available_fields(self):
        for rec in self:

            assignments = self.env['school.teacher.assignment'].search([
                ('teacher_id', '=', rec.teacher_id.id)
            ])

            rec.available_class_ids = assignments.mapped('class_id')

            # section filtered by selected class
            section_assignments = assignments
            if rec.class_id:
                section_assignments = assignments.filtered(
                    lambda a: a.class_id.id == rec.class_id.id
                )

            rec.available_section_ids = section_assignments.mapped('section_id')

            # subject filtered by selected class + section
            subject_assignments = section_assignments

            if rec.section_id:
                subject_assignments = section_assignments.filtered(
                    lambda a: a.section_id.id == rec.section_id.id
                )

            rec.available_subject_ids = subject_assignments.mapped('subject_id')

    #
    @api.constrains("exam_line_id")
    def _check_duplicate_exam_result(self):
        for rec in self:
            domain = [
                ('id','!=', rec.id),
                ('exam_line_id', '=', rec.exam_line_id)      
            ]
            if self.search_count(domain):
                raise ValidationError(_("This result is already submitted"))

    #auto load students
    @api.onchange('year_id','department_id', 'class_id', 'section_id')
    def _onchange_student_result(self):
        for rec in self:
            rec.result_ids = [(5,0,0)]

            enrollments = self.env['school.student.enrollment'].search([
                ('year_id', '=', rec.year_id.id),
                ('department_id', '=', rec.department_id.id),
                ('class_id', '=', rec.class_id.id),
                ('section_id', '=', rec.section_id.id)
            ])

            lines = []
            for enroll in enrollments:
                lines.append((0,0,{
                    'enrollment_id': enroll.id
                }))
            rec.result_ids = lines


    # code to filer classes by teacher assignment
    available_class_ids = fields.Many2many("school.class", compute="_compute_available_classes")
    @api.depends('teacher_id')
    def _compute_available_classes(self):
        for rec in self:
            if rec.teacher_id:
                assignments = self.env['school.teacher.assignment'].search([
                    ('teacher_id', '=', rec.teacher_id.id)
                ])
                rec.available_class_ids = assignments.mapped('class_id')
            else:
                rec.available_class_ids = [(5,0,0)]


    # code to filter sections by teacher and the selected class
    available_section_ids = fields.Many2many("school.class.section", compute="_compute_available_sections")
    @api.depends('teacher_id', 'class_id', 'department_id')
    def _compute_available_sections(self):
        for rec in self:
            if rec.teacher_id and rec.class_id and rec.department_id:
                assignments = self.env['school.teacher.assignment'].search([
                    ('teacher_id','=', rec.teacher_id.id),
                    ('class_id','=', rec.class_id.id),
                    ('department_id', '=', rec.department_id.id)
                ])
                rec.available_section_ids = assignments.mapped('section_id')
            else:
                rec.available_section_ids = [(5,0,0)]

    #filter subjects by teacher, department, class
    available_subject_ids = fields.Many2many("school.class.subject", compute="_compute_available_subjects")
    @api.depends('teacher_id', 'class_id', 'department_id')
    def _compute_available_subjects(self):
        for rec in self:
            if rec.teacher_id and rec.class_id and self.department_id:
                assignments = self.env['school.teacher.assignment'].search([
                    ('teacher_id','=', rec.teacher_id.id),
                    ('class_id', '=', rec.class_id.id),
                    ('department_id', '=', rec.department_id.id)
                ])
                rec.available_subject_ids = assignments.mapped('subject_id')
            else:
                rec.available_subject_ids = [(5,0,0)]
    

    
class SchoolExamResultLine(models.Model):
    _name = "school.exam.result.line"
    _description = "Student Results"

    result_id = fields.Many2one("school.exam.result", ondelete="cascade")

    enrollment_id = fields.Many2one(
        "school.student.enrollment",
        required=True
    )

    student_id = fields.Many2one(
        "school.student",
        related="enrollment_id.student_id",
        store=True,
        readonly=True
    )

    marks_obtained = fields.Float(string="Obtained Marks")
