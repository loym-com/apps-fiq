from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    folder_url = fields.Char(
        string="URL",
        related="documents_folder_id.url",
        readonly=False,
    )
