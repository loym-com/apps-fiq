# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplateAttributeValueCombiPrice(models.Model):
    _name = "product.template.attribute.value.combi.price"
    _description = "product.template.attribute.value.combi.price"

    ptav_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        string="Attribute Value",
        required=True,
        help="The attribute value to compute extra price for.",
        ondelete="cascade",
    )
    ptav_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        related="ptav_id.attribute_id",
    )
    ptav_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        related="ptav_id.product_tmpl_id",
    )
    condition_ptav_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        string="Conditional Attribute Value",
        required=True,
        help="The conditional attribute value.",
    )
    # price_extra_option = fields.Selection(
    #     selection=[
    #         ("fixed", "Add Fixed Extra Price"),
    #         ("percent", "Add Percent of Extra Price"),
    #     ],
    #     string="Extra Price Option",
    #     required=True,
    #     help="Choose how the extra price will be applied.",
    # )
    price_extra = fields.Float(
        string="Extra Price",
    )
    price_extra_percent = fields.Float(
        string="Extra Price %",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "condition_ptav_id" in fields_list:
            defaults["condition_ptav_id"] = False
        return defaults
