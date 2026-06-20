from odoo import models, api, fields


class SchoolTuitionFee(models.Model):
    _name = "school.tuition.fee"
    _description = "Tuition Fee Setup"

    year_id = fields.Many2one(
        "school.academic.year",
        required=True
    )

    department_id = fields.Many2one(
        "school.department",
        required=True
    )

    class_id = fields.Many2one(
        "school.class",
        required=True
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    monthly_fee = fields.Monetary(
        currency_field="currency_id",
        string="Monthly Fee"
    )

    active = fields.Boolean(
        default=True
    )

    _check_unique_fee = models.Constraint(
        'UNIQUE(year_id, department_id, class_id)',
        'Fee configuration already exists.'
    )


#create fees for a month
class SchoolFeeBatch(models.Model):
    _name = "school.fee.batch"
    _description = "Monthly Fee Batch"

    name = fields.Char(required=True)

    year_id = fields.Many2one(
        "school.academic.year",
        required=True
    )

    month_id = fields.Many2one(
        "school.month",
        required=True
    )

    last_date = fields.Date(
        required=True
    )

    line_ids = fields.One2many(
        "school.fee.batch.line",
        "batch_id",
        string="Students"
    )

    total_students = fields.Integer(
        compute="_compute_totals"
    )

    total_amount = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('closed', 'Closed')
    ], default='draft')

    _unique_batch = models.Constraint(
        'UNIQUE(year_id, month_id)',
        'Fee batch already exists for this month.'
    )

    @api.depends('line_ids.amount')
    def _compute_totals(self):
        for rec in self:
            rec.total_students = len(rec.line_ids)
            rec.total_amount = sum(
                rec.line_ids.mapped('amount')
            )

    def action_generate_students(self):

        self.ensure_one()

        self.line_ids = [(5, 0, 0)]

        enrollments = self.env[
            'school.student.enrollment'
        ].search([
            ('year_id', '=', self.year_id.id),
            ('state', '=', 'active')
        ])

        lines = []

        for enrollment in enrollments:

            fee = self.env[
                'school.tuition.fee'
            ].search([
                ('year_id', '=', enrollment.year_id.id),
                ('department_id', '=', enrollment.department_id.id),
                ('class_id', '=', enrollment.class_id.id),
            ], limit=1)

            lines.append((0, 0, {
                'enrollment_id': enrollment.id,
                'amount': fee.monthly_fee if fee else 0,
            }))

        self.line_ids = lines

        self.state = 'generated'



# each student monthly fees.
class SchoolFeeBatchLine(models.Model):
    _name = "school.fee.batch.line"
    _description = "Student Fee Line"

    batch_id = fields.Many2one(
        "school.fee.batch",
        required=True,
        ondelete="cascade"
    )

    enrollment_id = fields.Many2one(
        "school.student.enrollment",
        required=True
    )

    student_id = fields.Many2one(
        "school.student",
        related="enrollment_id.student_id",
        store=True
    )

    department_id = fields.Many2one(
        "school.department",
        related="enrollment_id.department_id",
        store=True
    )

    class_id = fields.Many2one(
        "school.class",
        related="enrollment_id.class_id",
        store=True
    )

    amount = fields.Monetary(
        currency_field="currency_id"
    )

    paid_amount = fields.Monetary(
        currency_field="currency_id"
    )

    due_amount = fields.Monetary(
        compute="_compute_due_amount",
        store=True,
        currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        related="batch_id.currency_id",
        store=True
    )

    state = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], compute="_compute_state", store=True)

    @api.depends('amount', 'paid_amount')
    def _compute_due_amount(self):
        for rec in self:
            rec.due_amount = rec.amount - rec.paid_amount

    @api.depends('amount', 'paid_amount')
    def _compute_state(self):
        for rec in self:

            if rec.paid_amount <= 0:
                rec.state = 'unpaid'

            elif rec.paid_amount >= rec.amount:
                rec.state = 'paid'

            else:
                rec.state = 'partial'