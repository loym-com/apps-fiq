import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Starting migration script for installing crm_name if needed")

    env['ir.module.module'].update_list()
    module = env['ir.module.module'].search([('name', '=', 'crm_name')], limit=1)
    if module:
        if module.state != 'installed':
            _logger.info("Installing module 'crm_name' (current state: %s)", module.state)
            module.button_install()
            env.cr.commit()
            _logger.info("Module 'crm_name' installed successfully")
        else:
            _logger.info("Module 'crm_name' already installed — skipping")
    else:
        _logger.warning("Module 'crm_name' not found after update_list()")

    _logger.info("Migration script for crm_name completed")
