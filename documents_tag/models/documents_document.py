from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    tag_id = fields.Many2one(
        comodel_name="documents.tag",
        string="Main Tag",
    )
    tag_tooltip_translate = fields.Char(
        string="Tag Tooltip",
        related="tag_id.tooltip_translate",
    )
