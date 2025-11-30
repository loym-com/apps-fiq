from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    documents_tag_id = fields.Many2one(
        comodel_name="documents.tag",
        string="Default Main Tag",
    )
    documents_tag_ids = fields.Many2many(
        comodel_name="documents.tag",
        string="Default Tags",
    )
    documents_tag_ids_filter = fields.Boolean(
        string="Default Tags Filter",
        default=True,
        store=False,
    )

    def _compute_documents_tag_ids_filter(self):
        self.documents_tag_ids_filter = True

    def _get_document_vals(self, attachment):
        vals = super()._get_document_vals(attachment)
        if self.documents_tag_id:
            vals['tag_id'] = self.documents_tag_id.id
        return vals
