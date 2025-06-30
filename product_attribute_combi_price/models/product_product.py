# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    price_extra = fields.Float(compute="_compute_product_price_extra")

    @api.depends(
        "product_template_attribute_value_ids.price_extra",
        "product_template_attribute_value_ids.combi_price_ids.price_extra",
        "product_template_attribute_value_ids.combi_price_ids.price_extra_percent",
    )
    def _compute_product_price_extra(self):
        super()._compute_product_price_extra()
        for product in self:
            product_extra = 0
            ptav_ids = product.product_template_attribute_value_ids
            # Attribute values have an "Extra Price" field.
            # An attribute combination may increase the "Extra Price" with a percentage.
            # Therefore 
            for ptav in ptav_ids:
                extra = 0
                combi_prices = product.product_template_attribute_value_ids.combi_price_ids
                for combi in combi_prices:
                    if combi.condition_ptav_id in product.product_template_attribute_value_ids:
                        if combi.price_extra:
                            extra += combi.price_extra
                        elif combi.price_extra_percent:
                            extra += (combi.ptav_id.price_extra * combi.price_extra_percent)
                product_extra += extra
            product.price_extra += product_extra
