from odoo import models, fields, api


class DocumentsTag(models.Model):
    _inherit = "documents.tag"

    parent_id = fields.Many2one(
        "documents.tag",
        string="Parent Tag",
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        "documents.tag",
        "parent_id",
        string="Child Tags",
    )

    tooltip_translate = fields.Char(
        string="Tooltip.",
        translate=True,
    )

    # TODO: Create a translate mixin based on documents_name/models/documents_document.py

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self._set_tooltip_or_tooltip_translate(vals)
        return super().create(vals_list)
    
    def write(self, vals):
        vals = self._set_tooltip_or_tooltip_translate(vals)
        return super().write(vals)
    
    def _set_tooltip_or_tooltip_translate(self, vals):
        if "tooltip_translate" in vals:
            vals["tooltip"] = vals["tooltip_translate"]
        elif "tooltip" in vals:
            vals["tooltip_translate"] = vals["tooltip"]
        return vals
