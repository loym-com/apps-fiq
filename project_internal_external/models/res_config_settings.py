from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_sequence_pattern = fields.Char(
        config_parameter="project_internal_external.project_sequence_pattern",
        readonly=False,
        string="Project No.",
    )
