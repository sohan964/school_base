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
    
    

    