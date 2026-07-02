# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import html2plaintext


class MailFiqInbox(models.AbstractModel):
    """Server side of the communication inbox flate.

    All methods run as the current user, so record rules apply: a user only
    sees messages and candidate elements they already have access to.
    """

    _name = "fiq.komm.inbox"
    _description = "FIQ communication inbox"

    @api.model
    def get_messages(self, limit=40):
        messages = self.env["mail.message"].search(
            [("message_type", "=", "email")],
            order="date desc", limit=limit)
        return [{
            "id": m.id,
            "author": m.author_id.display_name or m.email_from or "—",
            "subject": m.subject or self.env._("(no subject)"),
            "date": m.date and m.date.isoformat() or "",
            "preview": html2plaintext(m.body or "")[:160],
        } for m in messages]

    @api.model
    def get_message(self, message_id):
        m = self.env["mail.message"].browse(message_id).exists()
        if not m:
            return {}
        return {
            "id": m.id,
            "author": m.author_id.display_name or m.email_from or "—",
            "email_from": m.email_from or "",
            "subject": m.subject or "",
            "date": m.date and m.date.isoformat() or "",
            "body": m.body or "",
            "candidates": self.get_candidates(message_id),
        }

    @api.model
    def get_candidates(self, message_id):
        m = self.env["mail.message"].browse(message_id).exists()
        if not m:
            return []
        body = html2plaintext(m.body or "")
        return self.env["fiq.komm.match"].suggest(
            email_from=m.email_from, subject=m.subject, body=body,
            partner_id=m.author_id.id or False)

    @api.model
    def archive_to(self, message_id, model, res_id):
        """File the e-mail as a PDF (with metadata) on the chosen record."""
        m = self.env["mail.message"].browse(message_id).exists()
        target = self.env[model].browse(res_id).exists() if model else False
        if not (m and target):
            return False
        pdf, _dummy = self.env["ir.actions.report"]._render_qweb_pdf(
            "fiq_komm_inbox.report_mail_message", m.ids)
        attachment = self.env["ir.attachment"].create({
            "name": "%s.pdf" % (m.subject or self.env._("e-mail")),
            "type": "binary",
            "raw": pdf,
            "mimetype": "application/pdf",
            "res_model": model,
            "res_id": res_id,
        })
        if hasattr(target, "message_post"):
            target.message_post(
                body=self.env._(
                    "E-mail filed from communication inbox: %(subject)s (from %(sender)s)",
                    subject=m.subject or "", sender=m.email_from or ""),
                attachment_ids=attachment.ids)
        return {"attachment_id": attachment.id, "target": target.display_name}
