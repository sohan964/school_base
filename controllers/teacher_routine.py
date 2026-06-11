from odoo import http
from odoo.http import request


class TeacherRoutineController(http.Controller):

    @http.route(
        '/teacher/routine/pdf/<string:view_mode>',
        type='http',
        auth='user'
    )
    def teacher_routine_pdf(
        self,
        view_mode,
        **kwargs
    ):

        teacher = request.env['school.teacher'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        if not teacher:
            return request.not_found()

        report = request.env.ref(
            'school_base.action_report_teacher_routine'
        )

        pdf, _ = report._render_qweb_pdf(
            report.report_name,
            [teacher.id],
            data={
                'view_mode': view_mode,
            }
        )

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', str(len(pdf))),
            ]
        )