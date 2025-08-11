from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    name_translate = fields.Char(
        string="Name.",
        translate=True,
    )

    @api.onchange("name", "name_translate")
    @api.constrains("name", "name_translate")
    def _set_name_or_name_translate(self):
        for record in self:
            if record.name_translate and record.name_translate != record.name:
                record.name = record.name_translate
            elif record.name and record.name != record.name_translate:
                record.name_translate = record.name
