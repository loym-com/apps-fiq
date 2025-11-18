
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"
    _order = "name"

    @api.depends("sequence_code", "name")
    def _compute_sp_folder_name(self):
        for record in self:
            folder = record.documents_folder_id
            if folder:
                record.sp_folder_name = folder.display_name
            else:
                record.sp_folder_name = ""

    sp_folder_name = fields.Char(
        string="SP Folder Name",
        compute="_compute_sp_folder_name",
        help="Sharepoint folder name"
    )
