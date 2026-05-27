from odoo import models


class ProductTemplate(models.Model):
    _inherit = ["property.mixin", "product.template"]

    _properties_field = "product_properties"
