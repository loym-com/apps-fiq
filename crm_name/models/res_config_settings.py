from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    crm_lead_name_expression = fields.Char(
        config_parameter="crm_name.crm_lead_name_expression",
        readonly=False,
        string="Lead Name Pattern",
    )
    crm_lead_name_expression_triggers = fields.Char(
        config_parameter="crm_name.crm_lead_name_expression_triggers",
        readonly=False,
        string="Lead Name Pattern Triggers",
    )

    @api.constrains("crm_lead_name_expression", "crm_lead_name_expression_triggers")
    def _check_crm_lead_name_expression_and_triggers(self):
        Lead = self.env["crm.lead"]

        Lead.raise_error_if_invalid_field_paths_from_source(
            "ir.config_parameter", "crm_lead_name_expression"
        )

        triggers = self.crm_lead_name_expression_triggers
        if triggers:
            trigger_paths = [part.strip() for part in self.crm_lead_name_expression_triggers.split(",") if part.strip()]
            Lead.raise_error_if_invalid_field_paths(trigger_paths)
