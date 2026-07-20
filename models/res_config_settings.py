from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # for bkash integration
    bkash_base_url = fields.Char(
        string="bKash Base URL",
        config_parameter="school_base.base_url",
    )

    bkash_username = fields.Char(
        string="Username",
        config_parameter="school_base.username",
    )

    bkash_password = fields.Char(
        string="Password",
        config_parameter="school_base.password",
    )

    bkash_app_key = fields.Char(
        string="App Key",
        config_parameter="school_base.app_key",
    )

    bkash_app_secret = fields.Char(
        string="App Secret",
        config_parameter="school_base.app_secret",
    )