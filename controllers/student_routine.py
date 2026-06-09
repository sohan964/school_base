from odoo import http
from odoo.http import request


class StudentRoutineController(http.Controller):

    @http.route(
        '/student/routine/pdf/<string:view_mode>',
        type='http',
        auth='user'
    )
    def student_routine_pdf(
        self,
        view_mode,
        **kwargs
    ):

        student = request.env[
            'school.student'
        ].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        report = request.env.ref(
            'school_base.action_report_student_routine'
        )

        pdf, _ = report._render_qweb_pdf(
            report.report_name,
            [student.id],
            data={
                'view_mode': view_mode,
            }
        )

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
            ]
        )