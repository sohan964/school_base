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