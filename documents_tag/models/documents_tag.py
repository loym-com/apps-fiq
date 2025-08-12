from odoo import models, fields, api


class DocumentsTag(models.Model):
    _inherit = "documents.tag"

    tooltip_translate = fields.Char(
        string="Tooltip.",
        translate=True,
    )

    @api.onchange("tooltip_translate")
    @api.constrains("tooltip_translate")
    def _set_tooltip(self):
        for record in self:
            record.tooltip = record.tooltip_translate

    def _set_tooltip_translate(self):
        for record in self:
            record.tooltip_translate = record.tooltip