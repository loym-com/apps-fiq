from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"
    
    def action_document_link(self):
        """
        Go to the external URL of the folder/file.
        """
        if not self:
            return {}

        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
            "target": "new",
        }

    @api.onchange("url")
    def _compute_name_and_preview(self):
        """
        If name exists, do not update name based on URL.
        """
        if len(self) == 1 and self.url and self.name:
            return
        else:
            return super()._compute_name_and_preview()
