from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    name_translate = fields.Char(
        string="Name.",
        translate=True,
    )

    @api.onchange("name_translate")
    @api.constrains("name_translate")
    def _set_name(self):
        for record in self:
            record.name = record.name_translate

    def _set_name_translate(self):
        for record in self:
            record.name_translate = record.name
