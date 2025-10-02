from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    crm_lead_name_pattern = fields.Char(
        config_parameter="crm_name.crm_lead_name_pattern",
        readonly=False,
        string="Lead Name Pattern",
    )
    crm_lead_name_pattern_triggers = fields.Char(
        config_parameter="crm_name.crm_lead_name_pattern_triggers",
        readonly=False,
        string="Lead Name Pattern Triggers",
    )

    @api.constrains("crm_lead_name_pattern", "crm_lead_name_pattern_triggers")
    def _check_crm_lead_name_pattern_and_triggers(self):
        def _check_field_input(field_input):
            Lead = self.env["crm.lead"]
            if field_input:
                field_paths = Lead._get_display_field_paths_from_string(
                    field_input, validate=False
                )
                if not Lead._is_valid_display_field_paths(field_paths):
                    raise ValidationError(
                        f"_check_crm_lead_name_pattern_and_triggers: "
                        f"At least one field is not valid: {field_paths}"
                    )
        _check_field_input(self.crm_lead_name_pattern)
        _check_field_input(self.crm_lead_name_pattern_triggers)
