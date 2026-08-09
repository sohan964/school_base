from odoo import http
from odoo.http import request


class SchoolWebsiteController(http.Controller):

    @http.route(
        "/",
        type="http",
        auth="public",
        website=True,
    )
    def home(self):
        return request.render(
            "school_base.website_home"
        )