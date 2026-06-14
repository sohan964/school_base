from odoo import models
from datetime import date


class TeacherExamRoutineReport(models.AbstractModel):
    _name = 'report.school_base.teacher_exam_routine_report'
    _description = 'Teacher Exam Routine Report'

    def _get_report_values(
        self,
        docids,
        data=None
    ):

        teacher = self.env[
            'school.teacher'
        ].browse(docids)

        exam_id = data.get('exam_id')

        assignments = self.env[
            'school.teacher.assignment'
        ].search([
            ('teacher_id', '=', teacher.id)
        ])

        subject_ids = assignments.mapped(
            'subject_id'
        ).ids

        class_ids = assignments.mapped(
            'class_id'
        ).ids

        domain = [
            ('subject_id', 'in', subject_ids),
            ('class_id', 'in', class_ids),
        ]

        if exam_id:

            domain.append(
                ('exam_id', '=', exam_id)
            )

        else:

            today = date.today()

            domain.append(
                ('exam_date', '>=', today)
            )

        exams = self.env[
            'school.exam.line'
        ].search(
            domain,
            order='exam_date'
        )

        return {
            'docs': teacher,
            'teacher': teacher,
            'exams': exams,
        }