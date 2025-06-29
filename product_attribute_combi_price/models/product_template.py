# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ptav_combi_price_ids = fields.One2many(
        comodel_name="product.template.attribute.value.combi.price",
        inverse_name="ptav_tmpl_id",
        string="Attribute Value Combi Prices",
        help="List of attribute value combinations that affect the price.",
    )
