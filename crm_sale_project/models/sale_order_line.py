from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project(self):
        # name
        project = super()._timesheet_create_project()
        project._compute_name_from_settings()
        return project

    def _timesheet_create_project_prepare_values(self):
        project_values = super()._timesheet_create_project_prepare_values()
        project_values["user_id"] = self.order_id.user_id.id
        project_values["sale_order_id"] = self.order_id.id

        template = self.product_id.project_template_id

        try: # assignment_ids (OCA/project project_role)
            assignment_values = []
            for assignment in template.assignment_ids:
                dummy_salesperson_ref = "portal_user.res_users_dummy_salesperson"
                dummy_contact_ref = "portal_user.res_users_dummy_contact"
                if assignment.user_id == self.env.ref(dummy_salesperson_ref):
                    user = self.order_id.user_id
                    if not user:
                        raise UserError(
                            "There is no salesperson."
                        )
                elif assignment.user_id == self.env.ref(dummy_contact_ref):
                    user = self.order_id.partner_id.user_ids
                    if not user:
                        raise UserError(
                            "The contact is not a user. Tip: Grant portal access."
                        )
                else:
                    user = assignment.user_id
                assignment_values.append(
                    Command.create(
                        {
                            'company_id': self.order_id.company_id.id,
                            'role_id': assignment.role_id.id,
                            'user_id': user.id,
                        }
                    )
                )
            project_values["assignment_ids"] = assignment_values
        except AttributeError as e:
            pass # no attr assignment_ids

        return project_values
