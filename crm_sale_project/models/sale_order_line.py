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

        # user
        # default: 'user_id': self.product_id.project_template_id.user_id.id,
        # product_values["user_id"] = order.user_id.id

        # project.set_sequence_code_unique_code_and_name()

        template = self.product_id.project_template_id

        try: # assignment_ids (OCA/project project_role)
            assignment_values = []
            for assignment in template.assignment_ids:
                # user (public user ->> current user)
                if assignment.user_id == self.env.ref("base.public_user"):
                    user = self.env.user
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
        except:
            pass

        return project_values
