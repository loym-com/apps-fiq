from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.module.module'].update_list()
    module = env['ir.module.module'].search([('name', '=', 'crm_name')], limit=1)
    if module and module.state != 'installed':
        module.button_install()
        env.cr.commit()
