from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCrmLead(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "crm_name.crm_lead_name_expression",
            "{r.get_partner_name_and_project_address(' - ')}",
        )
        cls.lead = cls.env["crm.lead"].create(
            {
                "name": "/",
                "partner_name": "Contact Name",
                "project_address": "Project Address"
            }
        )
        cls.partner_id = cls.env["res.partner"].create(
            {"name": "Contact", "is_company": True}
        ).id
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Project",
                "type": "service",
                "sale_line_warn": "no-message",
            }
        )

    def test_name(self):
        self.assertEqual(self.lead.name, "Contact Name - Project Address")

    def test_create_sale_order_and_project_with_task_in_project(self):
        lead = self.lead
        self.product_template.service_tracking = "task_in_project"
        lead.sale_order_product_id = self.product_template.product_variant_ids.id
        lead.partner_id = self.partner_id

        lead.action_create_sale_order_and_project()

        correct_name = f"{lead.order_ids.name} {lead.name}"
        # Project name
        self.assertEqual(lead.sale_order_project_ids.name, correct_name)
        # Task name
        self.assertEqual(lead.sale_order_project_ids.task_ids.name, correct_name)

    def test_create_sale_order_and_project_with_task_global_project(self):

        def create_project(vals):
            # sale_timesheet
            vals.setdefault('billing_type', 'not_billable')
            return self.env['project.project'].create(vals)

        orig_project = create_project({"name": "Original Project"})
        lead_project = create_project({"name": "Lead Project"})

        product_template = self.product_template
        product_template.service_tracking = "task_global_project"
        product_template.project_id = orig_project.id
        lead = self.lead
        lead.sale_order_product_id = product_template.product_variant_ids.id
        lead.partner_id = self.partner_id
        lead.project_id = lead_project.id # depends on crm_timesheet

        lead.action_create_sale_order_and_project()

        self.assertEqual(lead.sale_order_project_ids, lead_project)
        self.assertEqual(product_template.project_id, orig_project)

        # Project name
        self.assertEqual(lead.sale_order_project_ids.name, lead_project.name)
        # Task name
        correct_name = f"{lead.order_ids.name} {lead.name}"
        self.assertEqual(lead.sale_order_project_ids.task_ids.name, correct_name)

    def test_crm_lead_valid_field_and_method(self):
        self.env["crm.lead"].raise_error_if_invalid_expression(
            "{r.id} {r.get_partner_name_and_project_address(' - ')}"
        )

    def test_crm_lead_invalid_field(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].raise_error_if_invalid_expression(
                "{r.non_existing_field}"
            )

    def test_crm_lead_invalid_method(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].raise_error_if_invalid_expression(
                "{r.non_existing_method()}"
            )
