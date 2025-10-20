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

    sale_order_product_id = fields.Many2one(
        "product.product",
        string="Sale Order Product",
        help="Product used when creating a sale order from the opportunity.",
    )
    sale_order_project_ids = fields.Many2many(
        "project.project",
        compute="_compute_sale_order_project_ids",
        string="Sale Order Projects",
    )
    sale_order_project_count = fields.Integer(
        compute="_compute_sale_order_project_count",
        string="Sale Order Project Count",
    )
    partner_short_name = fields.Char(
        related="partner_id.short_name",
        string="Short Name",
    )
    project = fields.Char()
