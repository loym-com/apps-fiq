from urllib.parse import urlencode

from odoo import api, fields, models, Command


class ProjectTask(models.Model):
    _inherit = "project.task"

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
        # Main tag
        if self.documents_tag_id:
            vals['tag_id'] = self.documents_tag_id.id
        elif self.project_id.documents_tag_id:
            vals['tag_id'] = self.project_id.documents_tag_id.id
        # Tags
        if self.documents_tag_ids:
            vals['tag_ids'] = [
                Command.link(tag.id)
                for tag in self.documents_tag_ids
            ]
        # else use project default tags
        return vals
