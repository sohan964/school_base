from datetime import datetime
from odoo import models


class TeacherRoutineReport(models.AbstractModel):
    _name = 'report.school_base.teacher_routine_report'
    _description = 'Teacher Routine Report'

    def _get_report_values(self, docids, data=None):

        teacher = self.env[
            'school.teacher'
        ].browse(docids).ensure_one()

        view_mode = data.get(
            'view_mode',
            'today'
        )

        domain = [
            ('teacher_id', '=', teacher.id)
        ]

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
            'docs': teacher,
            'routines': routines,
            'view_mode': view_mode,
        }