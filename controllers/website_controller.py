from odoo import http
from odoo.http import request
from odoo.tools import html2plaintext


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
        "/campus",
        type="http",
        auth="public",
        website=True,
    )
    def campus(self):
        return request.render("school_base.website_campus")

    @http.route(
        "/news",
        type="http",
        auth="public",
        website=True,
    )
    def news(self, event_type=None, **kwargs):
        allowed_types = {"news", "event", "notice"}
        selected_type = event_type if event_type in allowed_types else None
        domain = [
            ("active", "=", True),
            ("published", "=", True),
        ]
        if selected_type:
            domain.append(("event_type", "=", selected_type))

        events = request.env["school.event"].sudo().search(
            domain,
            order="event_date desc, id desc",
        )
        event_summaries = {
            event.id: (
                html2plaintext(event.description or "").strip()[:180]
            )
            for event in events
        }
        return request.render(
            "school_base.website_news",
            {
                "events": events,
                "event_summaries": event_summaries,
                "selected_type": selected_type,
            },
        )

    @http.route(
        "/news/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def news_detail(self, event_id, **kwargs):
        event = request.env["school.event"].sudo().search(
            [
                ("id", "=", event_id),
                ("active", "=", True),
                ("published", "=", True),
            ],
            limit=1,
        )
        if not event:
            return request.not_found()
        return request.render(
            "school_base.website_news_detail",
            {"event": event},
        )

    @http.route(
        "/contact",
        type="http",
        auth="public",
        website=True,
    )
    def contact(self, **kwargs):
        return request.render(
            "school_base.website_contact",
            {"company": request.website.company_id.sudo()},
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


    
    
