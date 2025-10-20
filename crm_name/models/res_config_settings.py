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

        def _check_fields(field_paths):
            if not Lead._is_valid_display_field_paths(field_paths):
                raise ValidationError(
                    f"_check_crm_lead_name_expression_and_triggers: "
                    f"At least one field is not valid: {field_paths}"
                )
        pattern_fields = Lead._get_display_field_paths("crm_lead_name_expression", "ir.config_parameter", validate=False)
        _check_fields(pattern_fields)
        trigger_fields = [part.strip() for part in self.crm_lead_name_expression_triggers.split(",") if part.strip()]
        _check_fields(trigger_fields)
