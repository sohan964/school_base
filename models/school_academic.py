from odoo import fields, models


class SchoolClass(models.Model):
    _name = "school.class"
    _description = "School Class"
    _order = "name"

    name = fields.Char(string="Class Name", required=True)
    code = fields.Char(string="Class Code", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("class_code_unique", "unique(code)", "Class code must be unique."),
        ("class_name_unique", "unique(name)", "Class name must be unique."),
    ]



class SchoolClassSection(models.Model):
    _name="school.class.section"
    _description="Sections under classes in the school"

    name=fields.Char(string="Section Name", required=True)
    code=fields.Char(string="Section Code", required=True)
    class_ids = fields.Many2many("school.class", "section_class_rel", "section_id", "class_id", string="Classes")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("section_code_unique", "unique(code)", "Section code must be unique"),
        ("section_name_unique", "unique(name)", "section name must be unique")
    ]


class SchoolClassSubject(models.Model):
    _name="school.class.subject"
    _description="subjects in class"

    name=fields.Char(string="Subject Name", required=True)
    code=fields.Char(string="Subject Code", required=True)
    class_ids = fields.Many2many("school.class", "subject_class_rel", "subject_id", "class_id", string="Classes")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("subject_code_unique", "unique(code)", "Subject code must be unique"),
    ]