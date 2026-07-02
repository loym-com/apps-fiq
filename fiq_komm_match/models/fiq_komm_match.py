# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import api, models
from odoo.tools import email_split


class FiqKommMatch(models.AbstractModel):
    """Categorization engine (v1, rule-based).

    Given an incoming message (sender, subject, body), suggest a ranked list of
    the Odoo elements it most likely belongs to — sales order, opportunity,
    project or task. Signals, accumulated per candidate:

      * reference in subject/body (e.g. an order number)      -> +60
      * the sender's own open items                           -> +50
      * a human-simple routing rule (fiq.komm.regel) matches  -> +40

    AI classification (type / urgency / semantic match) is layered on top in v2.
    Returns a list of dicts: {model, res_id, name, score, reason}.
    """

    _name = "fiq.komm.match"
    _description = "Communication categorization engine"

    # ------------------------------------------------------------------ public
    @api.model
    def suggest(self, email_from=None, subject=None, body=None,
                partner_id=None, limit=10):
        subject = subject or ""
        body = body or ""
        bucket = {}

        partner = False
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id).exists()
        if not partner and email_from:
            partner = self._find_partner(email_from)

        # 1. reference in subject/body (strongest single signal)
        for rec in self._reference_scan("%s %s" % (subject, body)):
            self._add(bucket, rec, 60, self.env._("Reference in subject/text"))

        # 2. sender's open items
        if partner:
            for rec in self._partner_open_items(partner):
                self._add(bucket, rec, 50, self.env._("Open item for the sender"))

        # 3. human-simple rules
        for regel in self._matching_rules(email_from, subject, body):
            for rec in self._rule_targets(regel, partner):
                self._add(bucket, rec, 40,
                          self.env._("Rule: %s", regel.name))

        ranked = sorted(bucket.values(), key=lambda d: -d["score"])
        return ranked[:limit]

    # --------------------------------------------------------------- internals
    @api.model
    def _find_partner(self, email_from):
        addresses = email_split(email_from or "")
        if not addresses:
            return False
        return self.env["res.partner"].search(
            [("email", "=ilike", addresses[0])], limit=1)

    @api.model
    def _partner_open_items(self, partner):
        recs = []
        partners = (partner | partner.commercial_partner_id)
        pids = partners.ids

        if "sale.order" in self.env:
            recs += self.env["sale.order"].search(
                [("partner_id", "in", pids),
                 ("state", "in", ("draft", "sent", "sale"))],
                order="write_date desc", limit=5)
        if "crm.lead" in self.env:
            recs += self.env["crm.lead"].search(
                [("partner_id", "in", pids), ("active", "=", True),
                 ("type", "=", "opportunity")],
                order="write_date desc", limit=5)
        recs += self.env["project.project"].search(
            [("partner_id", "in", pids)], order="write_date desc", limit=5)
        recs += self.env["project.task"].search(
            [("partner_id", "in", pids), ("active", "=", True)],
            order="write_date desc", limit=5)
        return recs

    @api.model
    def _matching_rules(self, email_from, subject, body):
        rules = self.env["fiq.komm.regel"].search(
            [("company_id", "in", (False, self.env.company.id))])
        return rules.filtered(
            lambda r: self._rule_matches(r, email_from, subject, body))

    @api.model
    def _rule_matches(self, regel, email_from, subject, body):
        value = (regel.condition_value or "").strip().lower()
        if not value:
            return False
        addresses = email_split(email_from or "")
        sender = (addresses[0].lower() if addresses else "")
        domain = sender.split("@")[-1] if "@" in sender else ""
        subject = (subject or "").lower()
        body = (body or "").lower()
        ctype = regel.condition_type
        if ctype == "sender_email":
            return sender == value
        if ctype == "sender_domain":
            return domain == value.lstrip("@")
        if ctype == "subject_contains":
            return value in subject
        if ctype == "body_contains":
            return value in body
        if ctype == "keyword":
            return value in subject or value in body
        return False

    @api.model
    def _rule_targets(self, regel, partner):
        if regel.target_type == "project" and regel.target_project_id:
            return [regel.target_project_id]
        if regel.target_type == "partner_open" and partner:
            return self._partner_open_items(partner)
        return []

    @api.model
    def _reference_scan(self, text):
        text = text or ""
        tokens = set(re.findall(r"\b\d{2,}[\d\-]*\b", text))          # 26-014, 00042
        tokens |= set(re.findall(r"\b[A-Za-z]{1,4}\d{3,}\b", text))   # S00042, INV0007
        recs = []
        for token in list(tokens)[:10]:
            if "sale.order" in self.env:
                recs += self.env["sale.order"].search(
                    [("name", "=ilike", token)], limit=3)
            recs += self.env["project.project"].search(
                [("name", "ilike", token)], limit=3)
        return recs

    # ------------------------------------------------------------------ helper
    @api.model
    def _add(self, bucket, record, score, reason):
        key = (record._name, record.id)
        entry = bucket.get(key)
        if entry:
            entry["score"] += score
            if reason not in entry["reason"]:
                entry["reason"] += " · " + reason
        else:
            bucket[key] = {
                "model": record._name,
                "res_id": record.id,
                "name": record.display_name,
                "score": score,
                "reason": reason,
            }
