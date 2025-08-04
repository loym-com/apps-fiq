from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    document_ids = fields.Many2many(
        "documents.document",
        compute="_compute_documents",
        string="Documents",
        store=True,
    )

    def _compute_documents(self):
        for project in self:
            project.document_ids = self.env["documents.document"].search([
                ("folder_id", "=", project.documents_folder_id.id)
            ])
