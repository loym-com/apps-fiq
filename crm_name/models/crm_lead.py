from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    partner_short_name = fields.Char(
        related="partner_id.short_name",
        string="Short Name",
    )

    @api.depends(
        lambda self: self._get_display_field_paths_from_string(
            self._get_display_pattern(
                "crm_name.crm_lead_name_pattern_triggers",
                source="ir.config_parameter"
            )
        )
    )
    def _compute_name(self):
        self.name = False
        self._set_field_from_pattern_name("name", "crm_name.crm_lead_name_pattern", source="ir.config_parameter")
