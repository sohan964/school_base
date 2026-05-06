from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SchoolExamType(models.Model):
    _name="school.exam.type"
    _description="All exam types"

    name=fields.Char(string="Exam Type")
    code=fields.Char(string="Exam Code")
    state=fields.Boolean(string="Status")


class SchoolExam(models.Model):
    _name="school.exam"
    _description="Exam for school"

    name = fields.Char(string="Exam Name")
    exam_type_id = fields.Many2one("school.exam.type",string="Exam Type")
    year_id = fields.Many2one("school.academic.year", string="Year")
    date_start = fields.Date(string="Date of Start")
    date_end = fields.Date(string="Date of end")
    state = fields.Selection([
        ('draft', "Draft"),
        ('running',"Running"),
        ('done',"Done"),
        ('cancelled',"Cancelled")
    ], string="Status")
    exam_line_ids = fields.One2many("school.exam.line",'exam_id', string="Exams")

    @api.constrains('exam_type_id', 'year_id')
    def _check_duplicate_exam(self):
        for rec in self:
            domain =[
                ('exam_type_id','=', rec.exam_type_id),
                ('year_id','=', rec.year_id)
            ]
            if self.search_count(domain):
                raise ValidationError("This Exam Already Created")

class SchoolExamLine(models.Model):
    _name="school.exam.line"
    _description="School Exams"

    exam_id = fields.Many2one("school.exam", string="Exam")
    department_id = fields.Many2one("school.department", string="Department")
    class_id = fields.Many2one("school.class", string="Class")
    subject_id = fields.Many2one("school.class.subject", string="Subject", domain="[('department_ids','=',department_id),('class_ids','=',class_id)]")
    exam_date = fields.Date(string="Exam Date")
    full_marks = fields.Float(string="Full Marks")
    exam_time_slot_id = fields.Many2one("school.exam.time.slot",string="Exam Time Slot")
    display_name = fields.Char(compute="_compute_display_name")
    # contrains remain
    # @api.constrains('')

    # display name
    @api.depends('exam_id', 'department_id', 'class_id', 'subject_id')
    def _compute_display_name(self):
        for rec in self:
            name = rec.exam_id.name or ""

            if rec.department_id:
                name += f" | {rec.department_id.name}"

            if rec.class_id:
                name += f" | {rec.class_id.name}"

            if rec.subject_id:
                name += f" | {rec.subject_id.name}"

            rec.display_name = name
    
    @api.constrains("department_id", "exam_id", "class_id", "subject_id", "exam_time_slot_id", "exam_date")
    def _check_duplicate_exam_line(self):
        for rec in self:

            # 1. Duplicate subject in same exam + class
            duplicate_domain = [
                ("id", "!=", rec.id),
                ("exam_id", "=", rec.exam_id.id),
                ("class_id", "=", rec.class_id.id),
                ("subject_id", "=", rec.subject_id.id),
            ]

            # duplicate_exam = self.search(duplicate_domain, limit=1)

            if self.search_count(duplicate_domain):
                raise ValidationError(
                    _("This subject is already assigned for this class in the selected exam.")
                )

            # 2. Time slot conflict
            conflict_domain = [
                ("id", "!=", rec.id),
                ("department_id", "=", rec.department_id.id),
                ("class_id", "=", rec.class_id.id),
                ("exam_date",'=', rec.exam_date),
                ("exam_time_slot_id", "=", rec.exam_time_slot_id.id),
            ]

            # conflict_exam = self.search(conflict_domain, limit=1)

            if self.search_count(conflict_domain):
                raise ValidationError(
                    _("Time slot conflict! Another exam is already scheduled for this department, class, and time slot.")
                )