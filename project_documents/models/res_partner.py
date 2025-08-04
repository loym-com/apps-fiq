from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    project_document_ids = fields.Many2many(
        "documents.document",
        compute="_compute_project_documents",
        string="Project Documents",
        store=True,
    )

    def _compute_project_documents(self):
        for partner in self:
            project_documents = self.env["documents.document"].search([
                ("folder_id", "=", partner.project_ids.documents_folder_id.id)
            ])
            partner.project_document_ids = project_documents
