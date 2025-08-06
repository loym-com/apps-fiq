from odoo import api, fields, models
from odoo.errors import UserError
from odoo.fields import Command


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.depends("order_ids")
    def _compute_sale_order_project_ids(self):
        for r in self:
            r["sale_order_project_ids"] = r.order_ids.mapped(lambda o: o.project_ids)

    @api.depends("order_ids")
    def _compute_sale_order_project_count(self):
        for r in self:
            r["sale_order_project_count"] = self.env["project.project"].search_count(
                [("sale_order_id.opportunity_id", "=", r.id)]
            )

    sale_order_project_ids = fields.Many2many(
        "project.project",
        compute="_compute_sale_order_project_ids",
        string="Sale Order Projects",
    )
    sale_order_project_count = fields.Integer(
        compute="_compute_sale_order_project_ids",
        string="Sale Order Projects",
    )

    def action_create_sale_order_and_project(self):
        self.ensure_one()
        
        # Get sale order product & project template from settings
        get_param = self.env["ir.config_parameter"].sudo().get_param
        product_id = get_param("crm_sale_project.sale_order_product_id")
        if product_id:
            product = self.env["product.product"].browse(int(product_id))
        else:
            raise UserError("Missing a product in Settings.")
        project_template_id = get_param("crm_sale_project.project_template_id")
        if project_template_id:
            template = self.env["project.project"].browse(int(project_template_id))
        else:
            raise UserError("Missing a project in Settings.")
        
        # Check other values
        if not self.partner_id: raise UserError("Missing a customer.")
        # if not self.company_id: raise UserError("Missing a company.")
        # if not self.campaign_id: raise UserError("Missing a campaign.")

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
            order.action_confirm()
            project = order.project_id
            project_values = {
                "name": f"{order.name} {order.partner_id.name}",
                "user_id": order.user_id.id,
                "type_id": template.type_id.id,
                "parent_id": template.parent_id.id,
                "internal_external": template.internal_external,
                "tag_ids": [Command.set(template.tag_ids.ids)],
                "allow_material": True, # Products on Tasks
                "allow_quotations": True, # Extra Quotations
                "allow_worksheets": True,
                "documents_tag_ids": [Command.set(template.document_tag_ids.ids)],,
                "worksheet_template_id": template.worksheet_template_id.id,
                "sale_line_id": order_line.id,
            }
            try:
                project_values["internal_external"] = template.internal_external
            except:
                pass
            project.write(project_values)
            project.set_sequence_code_unique_code_and_name()

            # assignment_default_values = {"company_id": order.company_id.id, "project_id": project.id}
            # assignment_list = [
            #     {"role_id": 2, "user_id": 7},                   # Eier: Christian
            #     {"role_id": 4, "user_id": order.user_id.id},    # Manager: user_id
            #     {"role_id": 12, "user_id": 6},                  # Deltager: Gjermund
            # ]
            # for assignment_values in assignment_list:
            #     self.env["project.assignment"].create(assignment_default_values | assignment_values)