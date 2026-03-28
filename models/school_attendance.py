from odoo import api, fields, models


class SchoolStudentAttendance(models.Model):
    _name = "school.student.attendance"
    _description = "Student Attendance Per Class"

    year_id = fields.Many2one("school.academic.year", string="Year")
    department_id = fields.Many2one("school.department",  string="Department")
    class_id = fields.Many2one("school.class", string="Class")
    section_id = fields.Many2one("school.class.section", string="Section", domain="[('department_id', '=', department_id), ('class_id','=', class_id)]")
    subject_id = fields.Many2one("school.class.subject", string="Subject", 
                                 domain="[('department_ids', '=', department_id), ('class_ids','=', class_id)]")
    teacher_assignment_id = fields.Many2one("school.teacher.assignment", string="Routine")




    