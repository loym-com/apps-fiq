from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    crm_sale_project_sale_order_product_id = fields.Many2one(
        "product.product",
        config_parameter="crm_sale_project.sale_order_product_id",
        readonly=False,
        string="Product for new order",
    )
    crm_sale_project_project_template_id = fields.Many2one(
        "project.project",
        config_parameter="crm_sale_project.project_template_id",
        readonly=False,
        string="Template for new project",
    )
