import logging

from odoo import models

from odoo.addons.base_display_name.tools import get_indexed_pattern

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "display.name.mixin"]

    def _compute_name_from_settings(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        name_pattern = get_param("crm_sale_project.project_name_pattern")
        if name_pattern:
                name = self._get_value_from_pattern(name_pattern)
                if name:
                    self.name = name
                else:
                    _logger.warning(
                        "Could not compute project name for project %s using pattern %s",
                        self.id,
                        name_pattern,
                    )
