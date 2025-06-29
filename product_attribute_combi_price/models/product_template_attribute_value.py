# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    combi_price_ids = fields.One2many(
        comodel_name="product.template.attribute.value.combi.price",
        inverse_name="ptav_id",
        string="Price Combinations",
        help="List of attribute value combinations that affect the price.",
        ondelete="cascade",
    )
