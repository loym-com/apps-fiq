from odoo import api, fields, models

from odoo.addons.crm.models import crm_lead

_old_compute_name = crm_lead.Lead._compute_name

def get_trigger_paths(self):
    xmlid = "crm_name.crm_lead_name_expression_triggers"
    paths = self.env["ir.config_parameter"].sudo().get_param(xmlid)
    if paths:
        return (path.strip() for path in paths.split(",") if path.strip())
    else:
        return ()

@api.depends(lambda self: get_trigger_paths(self))
def _patched_compute_name(self):
    """
    The original _compute_name() depends on "partner_id".
    The method is patched to get rid of this dependency.
    """
    for lead in self:
        lead.name = False
        lead.name = self.get_value_from_source(
            "ir.config_parameter", "crm_name.crm_lead_name_expression"
        )

crm_lead.Lead._compute_name = _patched_compute_name


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "expression.value.mixin"]

    partner_short_name = fields.Char(
        related="partner_id.short_name",
        string="Short Name",
    )
