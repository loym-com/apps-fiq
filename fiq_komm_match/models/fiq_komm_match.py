# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import api, models
from odoo.tools import email_split

# Kategori-bokser (front-modell): innhold-nøkkelord → kategori.
CATEGORY_KEYWORDS = {
    "Faktura": ["faktura", "efaktura", "e-faktura", "purring", "inkasso", "kreditnota", "betaling"],
    "Salg": ["tilbud", "prisforespørsel", "forespørsel", "pristilbud", "anbud", "offer"],
    "Våtrom": ["våtrom", "bad", "dusj", "membran", "sluk"],
    "Field Service": ["service", "befaring", "montering", "utrykning", "garanti"],
    "Ticket": ["support", "feil", "reklamasjon", "sak", "avvik", "mangel"],
}
# Innhold-type → oppgave-navn (nivå 2, SDVs faste faser).
TASK_KEYWORDS = {
    "Møter": ["møte", "referat", "byggemøte", "statusrapport"],
    "Endringer": ["endring", "endringsmelding", "em ", "tillegg", "revidert budsjett"],
    "Avvik": ["avvik", "mangel", "feil", "reklamasjon"],
    "Faktura": ["faktura", "betaling", "purring"],
    "Tegninger": ["tegning", "plan", "dwg", "snitt"],
    "Bestillinger": ["bestilling", "ordre", "leveranse", "bekreftelse"],
    "Inng tilbud": ["tilbud", "pristilbud", "prisforespørsel"],
    "Fremdrift": ["fremdrift", "bemanning", "ukesrapport", "oppstart"],
}


class FiqKommMatch(models.AbstractModel):
    """Kategoriserings-/pare-motor (v1.1 — Episteme-nivå).

    Per innkommende melding: klassifiser i kategori-BOKSER + rangér kandidat-elementer
    to-nivå (PROSJEKT → riktig OPPGAVE), med konfidens og variant-kontekst.

    Algoritmen (fra det gamle SuperOffice/Episteme-systemet + ekte SDV-data):
      avsender → domene → FIRMA + firma-kolleger → deres åpne prosjekter,
      recency-sortert (salg+prosjekt først). Adresse/bygg = sterkeste signal (fuzzy).
      Multi-match: adresse > kunde > fag/etasje > dato.

    Output (mater front-boksene):
      { categories: [..], candidates: [{model,res_id,name,score,confidence,task,variant,reason}],
        variant: '...', partner: {...} }
    """

    _name = "fiq.komm.match"
    _description = "Communication categorization engine"

    # ------------------------------------------------------------------ public
    @api.model
    def suggest(self, email_from=None, subject=None, body=None,
                partner_id=None, limit=8):
        subject = subject or ""
        body = body or ""
        text = "%s %s" % (subject, body)

        partner = False
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id).exists()
        if not partner and email_from:
            partner = self._find_partner(email_from)

        firm = self._firm_partners(partner)          # avsender + firma + kolleger

        bucket = {}
        # (1) Adresse/bygg i emne → prosjekt (STERKESTE, fuzzy) — +70
        for rec in self._address_scan(subject):
            self._add(bucket, rec, 70, self.env._("Address/building in subject"))
        # (2) Referanse (prosjektnr/ordrenr) i emne/tekst — +60
        for rec in self._reference_scan(text):
            self._add(bucket, rec, 60, self.env._("Reference in subject/text"))
        # (3) Firmaets (+ kollegers) åpne prosjekter/salg — +50
        for rec in self._firm_open_items(firm):
            self._add(bucket, rec, 50, self.env._("Open item for the sender's company"))
        # (4) Menneske-enkle regler — +40
        for regel in self._matching_rules(email_from, subject, body):
            for rec in self._rule_targets(regel, firm):
                self._add(bucket, rec, 40, self.env._("Rule: %s", regel.name))

        ranked = sorted(bucket.values(), key=lambda d: -d["score"])[:limit]

        # Nivå 2: finn riktig OPPGAVE i topp-prosjektene
        for c in ranked:
            c["confidence"] = self._confidence(c["score"])
            c["task"] = (self._match_task(c["res_id"], subject, body)
                         if c["model"] == "project.project" else None)

        variant = self._infer_variant(subject, body, ranked, firm)
        for c in ranked:
            c["variant"] = variant

        return {
            "categories": self._classify_categories(subject, body, ranked),
            "candidates": ranked,
            "variant": variant,
            "partner": ({"id": partner.id, "name": partner.display_name,
                         "firma": partner.commercial_partner_id.display_name}
                        if partner else False),
        }

    # --------------------------------------------------------- partner / firma
    @api.model
    def _find_partner(self, email_from):
        addresses = email_split(email_from or "")
        if not addresses:
            return False
        return self.env["res.partner"].search(
            [("email", "=ilike", addresses[0])], limit=1)

    @api.model
    def _firm_partners(self, partner):
        """Avsender + firma (commercial partner) + firma-kolleger (samme firma)."""
        if not partner:
            return self.env["res.partner"]
        firma = partner.commercial_partner_id or partner
        kolleger = self.env["res.partner"].search(
            [("commercial_partner_id", "=", firma.id)], limit=50)
        return partner | firma | kolleger

    @api.model
    def _firm_open_items(self, firm):
        if not firm:
            return []
        pids = firm.ids
        recs = []
        # Salg + prosjekt prioriteres (recency-sortert)
        if "sale.order" in self.env:
            recs += self.env["sale.order"].search(
                [("partner_id", "in", pids), ("state", "in", ("draft", "sent", "sale"))],
                order="write_date desc", limit=5)
        if "crm.lead" in self.env:
            recs += self.env["crm.lead"].search(
                [("partner_id", "in", pids), ("active", "=", True), ("type", "=", "opportunity")],
                order="write_date desc", limit=5)
        recs += self.env["project.project"].search(
            [("partner_id", "in", pids)], order="write_date desc", limit=8)
        return recs

    # --------------------------------------------------------- level-1 signals
    @api.model
    def _address_scan(self, subject):
        """Fuzzy adresse/bygg-match: ord-token i emnet → prosjektnavn (ilike).
        Bygg går igjen (HVII gt 5, Holmenveien 37, Sorgenfrigaten 10)."""
        subject = subject or ""
        # ord med 4+ tegn (gatenavn/byggnavn), samt tallgrupper (husnr)
        tokens = [t for t in re.findall(r"[A-Za-zÆØÅæøå]{4,}", subject)][:8]
        recs = []
        for token in tokens:
            recs += self.env["project.project"].search(
                [("name", "ilike", token)], limit=3)
        return recs

    @api.model
    def _reference_scan(self, text):
        text = text or ""
        tokens = set(re.findall(r"\b\d{2,}[\d\-]*\b", text))
        tokens |= set(re.findall(r"\b[A-Za-z]{1,4}\d{3,}\b", text))
        recs = []
        for token in list(tokens)[:10]:
            if "sale.order" in self.env:
                recs += self.env["sale.order"].search([("name", "=ilike", token)], limit=3)
            recs += self.env["project.project"].search([("name", "ilike", token)], limit=3)
        return recs

    # -------------------------------------------------------------- level-2 task
    @api.model
    def _match_task(self, project_id, subject, body):
        """Innhold-type → riktig eksisterende oppgave i prosjektet (ikke ny)."""
        text = ("%s %s" % (subject, body)).lower()
        Task = self.env["project.task"]
        for task_name, kws in TASK_KEYWORDS.items():
            if any(k in text for k in kws):
                task = Task.search(
                    [("project_id", "=", project_id), ("name", "ilike", task_name)], limit=1)
                if task:
                    return {"res_id": task.id, "name": task.display_name, "match": task_name}
        return None

    # ----------------------------------------------------- categories / variant
    @api.model
    def _classify_categories(self, subject, body, ranked):
        text = ("%s %s" % (subject, body)).lower()
        cats = []
        for cat, kws in CATEGORY_KEYWORDS.items():
            if any(k in text for k in kws):
                cats.append(cat)
        if any(c["model"] == "project.project" for c in ranked) and "Prosjekt" not in cats:
            cats.insert(0, "Prosjekt")
        return cats or [self.env._("Uparet")]

    @api.model
    def _infer_variant(self, subject, body, ranked, firm):
        text = ("%s %s" % (subject, body)).lower()
        has_project = any(c["model"] == "project.project" for c in ranked)
        sales_words = any(w in text for w in ("tilbud", "prisforespørsel", "forespørsel", "pris"))
        change_words = any(w in text for w in ("endring", "avvik", "møte", "faktura", "mangel"))
        if sales_words and not change_words:
            return self.env._("Salgs-fase (forespørsel/tilbud – kan være UE som vil gi bud)")
        if has_project and change_words:
            return self.env._("Eksisterende prosjekt (endring/avvik/oppfølging)")
        if not has_project:
            return self.env._("Usikker – ingen sikker match")
        return self.env._("Eksisterende prosjekt")

    @api.model
    def _confidence(self, score):
        if score >= 70:
            return self.env._("høy")
        if score >= 50:
            return self.env._("middels")
        return self.env._("lav")

    # ------------------------------------------------------------- human rules
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
    def _rule_targets(self, regel, firm):
        if regel.target_type == "project" and regel.target_project_id:
            return [regel.target_project_id]
        if regel.target_type == "partner_open" and firm:
            return self._firm_open_items(firm)
        return []

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
