from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project(self):
        # name
        project = super()._timesheet_create_project()
        if self.order_id.opportunity_id:
            project.name = f"{self.order_id.name} {self.order_id.opportunity_id.name}"
        return project

    def _timesheet_create_project_prepare_values(self):
        project_values = super()._timesheet_create_project_prepare_values()
        # Set user
        project_values["user_id"] = self.order_id.user_id.id
        # Set no parent
        if "parent_id" in self.env["project.project"]._fields:
            project_values["parent_id"] = False
        # Set assignments
        try: # assignment_ids (OCA/project project_role)
            template = self.product_id.project_template_id
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
            pass # no attr

        # sale_timesheet
        project_values.setdefault('billing_type', 'not_billable')

        return project_values

    def _timesheet_create_task(self, project):
        # Set name
        task = super()._timesheet_create_task(project)
        if self.order_id.opportunity_id:
            task.name = self._timesheet_get_task_name()
        return task

    def _timesheet_create_task_prepare_values(self, project):
        task_values = super()._timesheet_create_task_prepare_values(project)
        # Set user
        task_values["user_ids"] = [Command.set([self.order_id.user_id.id])]
        # Set no parent
        if "parent_id" in self.env["project.project"]._fields:
            task_values["parent_id"] = False
        return task_values

    def _timesheet_get_task_name(self):
        partner = self.order_partner_id
        return f"{self.product_id.name} - {partner.short_name or partner.name}"
