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
    project_address = fields.Char("Project Address")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals:
                vals["project_address"] = vals["name"]
            if "partner_name" in vals:
                vals["contact_name"] = vals["partner_name"]
        return super().create(vals_list)

    def get_partner_name_and_project_address(self, delimiter):
        self.ensure_one()
        result = []
        partner = self.partner_id
        if partner and partner.short_name:
            result.append(partner.short_name)
        elif partner and partner.name:
            result.append(partner.name)
        elif self.partner_name:
            result.append(self.partner_name)
        if self.project_address:
            result.append(self.project_address)
        return delimiter.join(result)

    def action_create_sale_order_and_project(self):
        self.ensure_one()
        
        # Get sale order PRODUCT >> project TEMPLATE
        product = self.sale_order_product_id
        if not product:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            product_id = get_param("crm_sale_project.sale_order_product_id")
            if product_id:
                product = self.env["product.product"].browse(int(product_id))
            else:
                raise UserError("Missing a sale order product (set on the lead or in Settings).")

        # Check other values
        if getattr(product.project_template_id, "is_fsm", False):
            raise UserError("The product's project template is for field service management. Please select another product.")
        if not self.partner_id: raise UserError("Missing a contact.")
        if not self.partner_id.is_company: raise UserError("Contact should be a company.")

        # Create
        if not self.sale_order_project_ids:
            if not self.company_id:
                raise UserError("Missing a salesperson.")
            order = self.env["sale.order"].create(
                {
                    "partner_id": self.partner_id.id, # Customer from the opportunity
                    "opportunity_id": self.id,        # Link to the opportunity
                    "company_id": self.company_id.id, # Company of the opportunity
                    "user_id": self.user_id.id,       # Salesman
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
