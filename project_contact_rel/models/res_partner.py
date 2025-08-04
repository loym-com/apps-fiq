from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    project_ids = fields.Many2many(
        "project.project",
        relation="project_contact_rel",
        string="Related Projects",
    )
