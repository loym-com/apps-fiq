from odoo import api, fields, models, Command


class PortalWizard(models.TransientModel):
    _inherit = "portal.wizard"

    def _send_email(self):
        if self.env.context.get("do_not_send_email"):
            return True
        else:
            return super()._send_email()
