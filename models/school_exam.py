from odoo import models, api, fields


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