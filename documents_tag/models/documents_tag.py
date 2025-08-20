from odoo import models, fields, api


class DocumentsTag(models.Model):
    _inherit = "documents.tag"

    tooltip_translate = fields.Char(
        string="Tooltip.",
        translate=True,
    )

    # @api.onchange("tooltip_translate")
    # @api.constrains("tooltip_translate")
    # def _set_tooltip(self):
    #     for record in self:
    #         record.tooltip = record.tooltip_translate

    # def _set_tooltip_translate(self):
    #     for record in self:
    #         record.tooltip_translate = record.tooltip

    @api.onchange("tooltip", "tooltip_translate")
    @api.constrains("tooltip", "tooltip_translate")
    def _set_tooltip_or_tooltip_translate(self):
        for record in self:
            if record.tooltip_translate and record.tooltip_translate != record.tooltip:
                record.tooltip = record.tooltip_translate
            elif record.tooltip and record.tooltip != record.tooltip_translate:
                record.tooltip_translate = record.tooltip
