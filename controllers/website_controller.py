from odoo import http
from odoo.http import request


class SchoolWebsite(http.Controller):

    @http.route(
        "/",
        type="http",
        auth="public",
        website=True,
    )
    def school_homepage(self, **kwargs):

        events = request.env["school.event"].sudo().search(
            [
                ("active", "=", True),
                ("published", "=", True),
            ],
            order="event_date desc, id desc",
            limit=3,
        )

        return request.render(
            "school_base.school_website_home",
            {
                "events": events,
            },
        )

    # about page
    @http.route(
        "/about",
        type="http",
        auth="public",
        website=True,
    )
    def about(self):
        return request.render(
            "school_base.website_about"
        )

    @http.route(
        "/academics",
        type="http",
        auth="public",
        website=True,
    )
    def academics(self):

        classes = request.env["school.class"].sudo().search(
            [
                ("active", "=", True),
            ],
            order="name",
        )

        exams = request.env["school.exam"].sudo().search(
            [
                ("state", "in", ["running"]),
            ],
            order="date_start asc",
        )

        return request.render(
            "school_base.website_academics",
            {
                "classes": classes,
                "exams": exams,
            }
        )


    @http.route(
        "/admissions",
        type="http",
        auth="public",
        website=True,
    )
    def admissions(self):
        return request.render(
            "school_base.website_admissions"
        )


    @http.route(
        "/school-test",
        type="http",
        auth="public",
        website=True,
    )
    def school_test(self):
        return request.render(
            "school_base.school_website_test"
        )


    
    