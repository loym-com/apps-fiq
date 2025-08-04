from odoo import models, fields, api

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    name_translate = fields.Char(
        string="Name.",
        translate=True,
    )

    @api.onchange("name_translate")
    def _onchange_name_translate(self):
        if self.name_translate:
            self.name = self.name_translate

    @api.constrains("name_translate")
    def _constrains_name_translate(self):
        for record in self:
            record.name = record.name_translate

    # @api.model
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if "name_translate" in vals and "name" not in vals:
    #             vals["name"] = vals["name_translate"]
    #     return super(YourModel, self).create(vals_list)

    # def write(self, vals):
    #     if "name_translate" in vals and "name" not in vals:
    #         vals["name"] = vals["name_translate"]
    #     return super().write(vals)
