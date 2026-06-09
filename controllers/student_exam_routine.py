from odoo import http
from odoo.http import request


class StudentExamRoutineController(http.Controller):

    @http.route(
        '/student/exam-routine/pdf/<int:exam_id>',
        type='http',
        auth='user'
    )
    def student_exam_routine_pdf(self, exam_id, **kwargs):

        student = request.env['school.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        report = request.env.ref(
            'school_base.action_report_exam_routine'
        )

        pdf, _ = report._render_qweb_pdf(
            report.report_name,
            [student.id],
            data={
                'exam_id': exam_id,
            }
        )

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
            ]
        )