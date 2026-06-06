from odoo import fields, models, api
from odoo.exceptions import ValidationError

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
    class_id = fields.Many2one("school.class", string="Classes", required=True)
    department_id = fields.Many2one("school.department", string="Department", required=True)
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
    department_ids = fields.Many2many("school.department", "subject_department_rel", "subject_id", "department_id", string="Departments")
    class_ids = fields.Many2many("school.class", "subject_class_rel", "subject_id", "class_id", string="Classes")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("subject_code_unique", "unique(code)", "Subject code must be unique"),
    ]



class SchoolTeacherAssignment(models.Model):
    _name="school.teacher.assignment"
    _description="assigning teachers for couses"

    teacher_id = fields.Many2one('school.teacher', string="Teacher", required=True)
    year_id = fields.Many2one('school.academic.year', string="Year", required=True )
    department_id = fields.Many2one("school.department", string="Department", required=True)
    class_id = fields.Many2one("school.class", string="Class", required=True)
    section_id = fields.Many2one("school.class.section", string='Section',
                                 domain="[('department_id', '=', department_id), ('class_id', '=', class_id)]", required=True)
    subject_id = fields.Many2one("school.class.subject", string="Subject",
                                 domain="[('department_ids', '=', department_id), ('class_ids', '=', class_id)]", required=True)
    day_id = fields.Many2one("school.weekly.day", string="Days", required=True)
    slot_id = fields.Many2one("school.time.slot", string="Slots", required=True)

    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends('class_id', 'section_id', 'subject_id', 'day_id', 'slot_id')
    def _compute_display_name(self):
        for rec in self:
            name = rec.class_id.name or ""

            if rec.section_id:
                name += f" | {rec.section_id.name}"

            if rec.subject_id:
                name += f" | {rec.subject_id.name}"

            if rec.day_id and rec.slot_id:
                name += f" | {rec.day_id.name} ({rec.slot_id.name})"

            rec.display_name = name

    # Prevent assigning the same subject of a class-section
    # to multiple teachers in the same academic year.
    @api.constrains(
        'year_id',
        'class_id',
        'section_id',
        'subject_id',
        'teacher_id'
    )
    def _check_subject_teacher_conflict(self):

        for rec in self:

            domain = [
                ('id', '!=', rec.id),
                ('year_id', '=', rec.year_id.id),
                ('class_id', '=', rec.class_id.id),
                ('section_id', '=', rec.section_id.id),
                ('subject_id', '=', rec.subject_id.id),
                ('teacher_id', '!=', rec.teacher_id.id)
            ]

            existing = self.search(domain, limit=1)

            if existing:
                raise ValidationError(
                    f"""
                    Subject '{rec.subject_id.name}'
                    for Class '{rec.class_id.name}'
                    Section '{rec.section_id.name}'
                    is already assigned to another teacher
                    in this academic year.
                    """
                )

    @api.constrains('year_id','teacher_id', 'day_id', 'slot_id')
    def _check_teacher_conflict(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('year_id', '=', rec.year_id.id),
                ('teacher_id', '=', rec.teacher_id.id),
                ('day_id', '=', rec.day_id.id),
                ('slot_id', '=', rec.slot_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError("Teacher already assigned in this time slot for the year.")
    

    @api.constrains('year_id','class_id', 'section_id', 'day_id', 'slot_id')
    def _check_class_section_conflict(self):
        for rec in self:
            if not (rec.class_id and rec.section_id and rec.day_id and rec.slot_id):
                continue

            domain = [
                ('id', '!=', rec.id),
                ('year_id', '=', rec.year_id.id),
                ('class_id', '=', rec.class_id.id),
                ('section_id', '=', rec.section_id.id),
                ('day_id', '=', rec.day_id.id),
                ('slot_id', '=', rec.slot_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    "This class and section already has a subject at this day and time slot!"
                )

    # this is for student get rutine record rules
    student_user_ids = fields.Many2many(
        "res.users",
        compute="_compute_student_user_ids",
        store=True,
    )
    
    @api.depends('class_id', 'section_id', 'year_id')
    def _compute_student_user_ids(self):
        Enrollment = self.env['school.student.enrollment']

        for rec in self:
            enrollments = Enrollment.search([
                ('class_id', '=', rec.class_id.id),
                ('section_id', '=', rec.section_id.id),
                ('year_id', '=', rec.year_id.id),
            ])

            rec.student_user_ids = enrollments.mapped('student_id.user_id')
        
    # _sql_constraints = [

    #     # 1. Teacher cannot be in two places at same time
    #     (
    #         "teacher_time_conflict",
    #         "unique(teacher_id, day_id, slot_id)",
    #         "This teacher already has a class at this day and time slot!",
    #     ),

    #     # 2. Same class+section cannot have two subjects at same time
    #     (
    #         "class_section_time_conflict",
    #         "unique(class_id, section_id, day_id, slot_id)",
    #         "This class and section already has a subject at this day and time slot!",
    #     ),

    #     # 3. Optional: Same subject shouldn't repeat same time (extra safety)
    #     (
    #         "subject_time_conflict",
    #         "unique(subject_id, class_id, section_id, day_id, slot_id)",
    #         "This subject is already assigned at this time!",
    #     ),
    # ]