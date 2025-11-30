from odoo import fields, models


class DocumentsTagMixin(models.AbstractModel):
    _name = "documents.tag.mixin"
    _description = "documents.tag.mixin"

    documents_tag_id = fields.Many2one(
        comodel_name="documents.tag",
        string="DOC Main Tag",
    )
    documents_tag_ids = fields.Many2many(
        comodel_name="documents.tag",
        string="DOC Tags",
    )
    documents_tag_ids_filter = fields.Boolean(
        string="DOC Tags Filter",
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
