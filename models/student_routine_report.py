from odoo import models
from datetime import datetime


class StudentRoutineReport(models.AbstractModel):
    _name = "report.school_base.student_routine_report"

    def _get_report_values(
        self,
        docids,
        data=None
    ):

        student = self.env[
            'school.student'
        ].browse(docids).ensure_one()

        enrollment = self.env[
            'school.student.enrollment'
        ].search([
            ('student_id', '=', student.id),
            ('state', '=', 'active')
        ], limit=1)

        domain = [
            ('department_id', '=', enrollment.department_id.id),
            ('class_id', '=', enrollment.class_id.id),
            ('section_id', '=', enrollment.section_id.id),
            ('year_id', '=', enrollment.year_id.id),
        ]

        view_mode = data.get(
            'view_mode',
            'today'
        )

        if view_mode == 'today':

            today_name = datetime.today().strftime('%A')

            domain.append(
                ('day_id.name', '=', today_name)
            )

        routines = self.env[
            'school.teacher.assignment'
        ].search(
            domain,
            order='day_id, slot_id'
        )

        return {
            'docs': student,
            'enrollment': enrollment,
            'routines': routines,
            'view_mode': view_mode,
        }