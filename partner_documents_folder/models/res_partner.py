from urllib.parse import urlencode

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_folder_id = fields.Many2one(
        "documents.document",
        string="Contact Internal Folder",
    )
    customer_folder_id = fields.Many2one(
        "documents.document",
        string="Customer Internal Folder",
    )
    supplier_folder_id = fields.Many2one(
        "documents.document",
        string="Supplier Internal Folder",
    )

    partner_folder_url = fields.Char(
        string="Contact External URL",
        related="partner_folder_id.url",
        readonly=False,
    )
    customer_folder_url = fields.Char(
        string="Customer External URL",
        related="customer_folder_id.url",
        readonly=False,
    )
    supplier_folder_url = fields.Char(
        string="Supplier External URL",
        related="supplier_folder_id.url",
        readonly=False,
    )

    @api.constrains("partner_folder_url")
    def _constrains_partner_folder_url(self):
        if self.partner_folder_url and not self.partner_folder_id:
            root = "partner_documents_folder.documents_document_partner_folder"
            self.partner_folder_id = self.env["documents.document"].create(
                {
                    "name": self.name,
                    "url": self.partner_folder_url,
                    "type": "folder",
                    "partner_id": self.id,
                    "folder_id": self.env.ref(root).id,
                }
            )

    @api.constrains("customer_folder_url")
    def _constrains_customer_folder_url(self):
        if self.customer_folder_url and not self.customer_folder_id:
            root = "partner_documents_folder.documents_document_customer_folder"
            self.customer_folder_id = self.env["documents.document"].create(
                {
                    "name": self.name,
                    "url": self.customer_folder_url,
                    "type": "folder",
                    "partner_id": self.id,
                    "folder_id": self.env.ref(root).id,
                }
            )

    @api.constrains("supplier_folder_url")
    def _constrains_supplier_folder_url(self):
        if self.supplier_folder_url and not self.supplier_folder_id:
            root = "partner_documents_folder.documents_document_supplier_folder"
            self.supplier_folder_id = self.env["documents.document"].create(
                {
                    "name": self.name,
                    "url": self.supplier_folder_url,
                    "type": "folder",
                    "partner_id": self.id,
                    "folder_id": self.env.ref(root).id,
                }
            )

    def action_goto_documents(self):
        self.ensure_one()
        contact_type = self.env.context.get("contact_type")
        internal_external = self.env.context.get("internal_external")
        folder = getattr(self, contact_type + "_folder_id")
        if internal_external == "internal":
            domain = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            params = {
                'action': self.env.ref("documents.document_action").id,
                'menu_id': self.env.ref("documents.menu_root").id,
                'model': 'documents.document',
                'documents_init_folder_id': folder.id
            }
            url = f"{domain}/web#{urlencode(params)}"
        else:
            url = folder.url
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
