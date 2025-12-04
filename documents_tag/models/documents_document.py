from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _name = "documents.document"
    _inherit = ["documents.document", "documents.tag.mixin"]

    tag_id = fields.Many2one(
        comodel_name="documents.tag",
        string="Main Tag",
    )
    tag_tooltip_translate = fields.Char(
        string="Tag Tooltip",
        related="tag_id.tooltip_translate",
    )
    tag_all_child_ids = fields.Many2many(
        'documents.tag',
        related="tag_id.all_child_ids",
        string="DOC All Children",
    )
    tag_ids_filter = fields.Boolean(
        string="Tags Filter",
        default=True,
        store=False,
    )
    tag_color = fields.Integer(string="Tag Color Index", related="tag_id.color")
