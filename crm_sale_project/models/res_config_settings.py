from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    crm_sale_project__sale_order_product_id = fields.Many2one(
        "product.product",
        config_parameter="crm_sale_project.sale_order_product_id",
        readonly=False,
        string="Product for new order",
    )
    crm_sale_project__project_name_pattern = fields.Char(
        config_parameter="crm_sale_project.project_name_pattern",
        readonly=False,
        string="Name for new project",
    )

