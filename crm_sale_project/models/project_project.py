from odoo import models

from odoo.addons.base_display_name.tools import get_indexed_pattern


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _compute_name_from_settings(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        name_pattern = get_param("crm_sale_project.project_name_pattern")
        if name_pattern:
            field_paths = self._get_display_field_paths_from_pattern(name_pattern)
            if field_paths:
                indexed_pattern = get_indexed_pattern(name_pattern, field_paths)
                name = self._get_value_from_indexed_pattern(
                    self, field_paths, indexed_pattern
                )
                self.name = name
