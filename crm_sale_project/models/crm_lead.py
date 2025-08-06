from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.depends("order_ids")
    def _compute_sale_order_project_ids(self):
        for r in self:
            r.sale_order_project_ids = r.order_ids.mapped(lambda o: o.project_ids).ids

    @api.depends("order_ids")
    def _compute_sale_order_project_count(self):
        for r in self:
            r.sale_order_project_count = self.env["project.project"].search_count(
                [("sale_order_id.opportunity_id.id", "=", r.id)]
            )

    sale_order_project_ids = fields.Many2many(
        "project.project",
        compute="_compute_sale_order_project_ids",
        string="Sale Order Projects",
    )
    sale_order_project_count = fields.Integer(
        compute="_compute_sale_order_project_count",
        string="Sale Order Projects",
    )

    def action_create_sale_order_and_project(self):
        self.ensure_one()
        
        # Get sale order PRODUCT & project TEMPLATE from settings
        get_param = self.env["ir.config_parameter"].sudo().get_param
        product_id = get_param("crm_sale_project.sale_order_product_id")
        if product_id:
            product = self.env["product.product"].browse(int(product_id))
        else:
            raise UserError("Missing a product in Settings.")
        
        # Check other values
        if not self.partner_id: raise UserError("Missing a contact.")

        # Create
        if not self.sale_order_project_ids:
            order = self.env["sale.order"].create(
                {
                    "partner_id": self.partner_id.id, # Customer from the opportunity
                    "opportunity_id": self.id,        # Link to the opportunity
                    "company_id": self.company_id.id,  # Company of the opportunity
                    "user_id": self.user_id.id,          # Salesman
                    "campaign_id": self.campaign_id.id,
                    "medium_id": self.medium_id.id,
                    "source_id": self.source_id.id,
                }
            )
            order_line = self.env["sale.order.line"].create(
                {
                    "order_id": order.id,
                    "name": order.partner_id.display_name,
                    "product_id": product.id,
                }
            )
            order.action_confirm() # will create project
