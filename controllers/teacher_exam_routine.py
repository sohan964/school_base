from odoo import http
from odoo.http import request


class TeacherExamRoutineController(http.Controller):

    @http.route(
        '/teacher/exam/routine/pdf/<int:exam_id>',
        type='http',
        auth='user'
    )
    def teacher_exam_routine_pdf(
        self,
        exam_id,
        **kwargs
    ):

        teacher = request.env[
            'school.teacher'
        ].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        report = request.env.ref(
            'school_base.action_report_teacher_exam_routine'
        )

        pdf, _ = report._render_qweb_pdf(
            report.report_name,
            [teacher.id],
            data={
                'exam_id': exam_id
            }
        )

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
            ]
        )