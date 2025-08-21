from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    name_translate = fields.Char(
        string="Name.",
        translate=True,
    )

    # TODO: New module base_new_field_translate with mixin to handle this
    # Use a new field name_translate or in-place update name field (needs uninstall hook)?

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self._set_name_or_name_translate(vals)
        return super().create(vals_list)
    
    def write(self, vals):
        vals = self._set_name_or_name_translate(vals)
        return super().write(vals)
    
    def _set_name_or_name_translate(self, vals):
        if "name_translate" in vals:
            vals["name"] = vals["name_translate"]
        elif "name" in vals:
            vals["name_translate"] = vals["name"]
        return vals
