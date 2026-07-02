# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

CONDITION_TYPES = [
    ("sender_email", "Sender e-mail is"),
    ("sender_domain", "Sender domain is"),
    ("subject_contains", "Subject contains"),
    ("body_contains", "Message text contains"),
    ("keyword", "Subject or text contains keyword"),
]

TARGET_TYPES = [
    ("partner_open", "Sender's open items (automatic)"),
    ("project", "A specific project"),
]


class FiqKommRegel(models.Model):
    """Human-simple routing rule: a non-technical user states, in plain words,
    which element an incoming message most likely belongs to.

    Example: "IF sender domain is @lysglint.no THEN the sender's open items"
             "IF subject contains 26-014 THEN project Norvik".
    The engine (fiq.komm.match) reads active rules and boosts matching candidates.
    """

    _name = "fiq.komm.regel"
    _description = "Communication routing rule"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=False)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(
        default=10, help="Lower number = evaluated first (higher priority).")
    company_id = fields.Many2one(
        "res.company", string="Company", index=True,
        default=lambda self: self.env.company)

    condition_type = fields.Selection(
        CONDITION_TYPES, required=True, default="sender_domain",
        help="What to look at in the incoming message.")
    condition_value = fields.Char(
        required=True,
        help="The value to look for, e.g. 'lysglint.no', '26-014' or 'tilbud'.")

    target_type = fields.Selection(
        TARGET_TYPES, required=True, default="partner_open",
        help="Where the message should be suggested when the rule matches.")
    target_project_id = fields.Many2one(
        "project.project", string="Target project", ondelete="cascade")
