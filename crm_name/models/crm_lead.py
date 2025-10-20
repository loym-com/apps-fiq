from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    partner_short_name = fields.Char(
        related="partner_id.short_name",
        string="Short Name",
    )

    @api.depends(lambda self: self.get_field_paths_from_source(
        "ir.config_parameter", "crm_name.crm_lead_name_expression_triggers")
    )
    def _compute_name(self):
        self.name = False
        self.name = self.get_value_from_source("ir.config_parameter", "crm_name.crm_lead_name_expression")
