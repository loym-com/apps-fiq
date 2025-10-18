from odoo import api, fields, models


class ResCity(models.Model):
    _inherit = "res.city"

    def _compute_display_name(self):
        for r in self:
            if r.state_id:
                name = f"{r.name}, {r.state_id.name}, {r.country_id.name}"
            else:
                name = f"{r.name}, {r.country_id.name}"
            r.display_name = name

    assign_location_ids = fields.One2many(
        "res.partner.assign.location",
        "city_id",
        string="Assigned Locations",
    )
