from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_documents_folder_url = fields.Char(
        string="Project URL",
        related="project_id.documents_folder_id.url",
    )
