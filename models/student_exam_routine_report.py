from odoo import models


class StudentExamRoutineReport(models.AbstractModel):
    _name = 'report.school_base.student_exam_routine_report'
    _description = 'Student Exam Routine Report'

    def _get_report_values(self, docids, data=None):

        student = self.env['school.student'].browse(docids).ensure_one()

        exam_id = data.get('exam_id')

        enrollment = self.env[
            'school.student.enrollment'
        ].search([
            ('student_id', '=', student.id),
            ('state', '=', 'active')
        ], limit=1)

        domain = [
            ('department_id', '=', enrollment.department_id.id),
            ('class_id', '=', enrollment.class_id.id),
        ]

        if exam_id:
            domain.append(
                ('exam_id', '=', exam_id)
            )

        exam_lines = self.env[
            'school.exam.line'
        ].search(
            domain,
            order='exam_date asc'
        )

        return {
            'doc_ids': docids,
            'doc_model': 'school.student',
            'docs': student,
            'exam_lines': exam_lines,
            'enrollment': enrollment,
        }