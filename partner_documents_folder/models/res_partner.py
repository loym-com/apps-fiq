from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_folder_id = fields.Many2one(
        "documents.document",
        string="Contact Folder",
    )
    customer_folder_id = fields.Many2one(
        "documents.document",
        string="Customer Folder",
    )
    supplier_folder_id = fields.Many2one(
        "documents.document",
        string="Supplier Folder",
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
                    "folder_id": self.env.ref(root).id,
                }
            )
