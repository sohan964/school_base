from odoo import models, fields


class SchoolEvent(models.Model):
    _name = "school.event"
    _description = "School News & Event"
    _order = "event_date desc, id desc"

    name = fields.Char(
        string="Title",
        required=True,
    )

    description = fields.Html(
        string="Description",
    )

    image = fields.Image(
        string="Image",
    )

    event_date = fields.Date(
        string="Date",
        required=True,
    )

    event_type = fields.Selection(
        selection=[
            ("news", "News"),
            ("event", "Event"),
            ("notice", "Notice"),
        ],
        string="Type",
        required=True,
        default="event",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    published = fields.Boolean(
        string="Published",
        default=False,
    )