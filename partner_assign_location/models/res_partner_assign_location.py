from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerAssignLocation(models.Model):
    _name = "res.partner.assign.location"
    _description = "res.partner.assign.location"

    @api.depends("location_field", "zip_id", "city_id", "state_id", "country_id")
    def _compute_name(self):
        for record in self:
            if record.location_field == "zip_id" and record.zip_id:
                record.name = record.zip_id.display_name
            elif record.location_field == "city_id" and record.city_id:
                record.name = record.city_id.display_name
            elif record.location_field == "state_id" and record.state_id:
                record.name = record.state_id.display_name
            elif record.location_field == "country_id" and record.country_id:
                record.name = record.country_id.display_name
            else:
                record.name = "Undefined"

    name = fields.Char(
        string="Name",
        compute="_compute_name",
    )
    location_field = fields.Selection(
        [
            ("zip_id", "Zip"),
            ("city_id", "City"),
            ("state_id", "State"),
            ("country_id", "Country"),
        ],
        string="Location Field",
        required=True,
    )
    zip_id = fields.Many2one(
        "res.city.zip",
        string="zip_id",
        required=True,
    )
    city_id = fields.Many2one(
        "res.city",
        string="city_id",
        required=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="state_id",
        required=True,
    )
    country_id = fields.Many2one(
        "res.country",
        string="country_id",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
    )
    is_exclusive = fields.Boolean(
        string="Exclusive",
        help="If checked, this location will only be assigned to this contact.",
    )
    active = fields.Boolean(
        string="Active",
    )

    @api.constrains("partner_id", "is_exclusive", "location_field", "zip_id", "city_id", "state_id", "country_id", "active")
    def _check_exclusive(self):
        """ Ensure no conflicting assignments. """
        if not any(record.active for record in self):
            return

        self.ensure_one()

        fields = ["zip_id", "city_id", "state_id", "country_id"]
        i = fields.index(self.location_field)

        # The location_field will determine how specific the search is.
        # If the current record is assigned to a zip, search for conflicing zip/city/state/country.
        # If the current record is assigned to a country, search for conflicting country
        # (the location_field may be zip/city/state/country).
        search_fields = fields[i:]
        location_fields = fields[:i+1]

        # Build the domain dynamically
        domain = [("id", "!=", self.id)]
        domain += ["|"] * (len(search_fields) - 1)
        for search_field in search_fields:
            location_fields = location_fields or [search_field]
            domain += [
                "&",
                ("location_field", "in", location_fields),
                (search_field, "=", getattr(self, search_field).id)
            ]
            location_fields = None

        existing = self.search(domain)
        exclusive = existing.filtered(lambda r: r.is_exclusive)
        if exclusive:
            names = ", ".join(existing.mapped("partner_id").mapped("name"))
            raise ValidationError(
                f"This assignment conflicts with assignments to {names}"
            )
        if self.is_exclusive:
            non_exclusive = existing - exclusive
            non_exclusive.write({"active": False})
        
        # Build the domain dynamically
        # should produce the same domains as below:

        # domain_zip = [
        #     ("id", "!=", self.id),
        #     "|", "|", "|",
        #     "&", ("location_field", "=", "zip_id"), ("zip_id", "=", self.zip_id.id),
        #     "&", ("location_field", "=", "city_id"), ("city_id", "=", self.city_id.id),
        #     "&", ("location_field", "=", "state_id"), ("state_id", "=", self.state_id.id),
        #     "&", ("location_field", "=", "country_id"), ("country_id", "=", self.country_id.id),
        # ]
        # domain_city = [
        #     ("id", "!=", self.id),
        #     "|", "|",
        #     "&", ("location_field", "in", ["zip_id", "city_id"]), ("city_id", "=", self.city_id.id),
        #     "&", ("location_field", "=", "state_id"), ("state_id", "=", self.state_id.id),
        #     "&", ("location_field", "=", "country_id"), ("country_id", "=", self.country_id.id),
        # ]
        # domain_state = [
        #     ("id", "!=", self.id),
        #     "|",
        #     "&", ("location_field", "in", ["zip_id", "city_id", "state_id"]), ("state_id", "=", self.state_id.id),
        #     "&", ("location_field", "=", "country_id"), ("country_id", "=", self.country_id.id),
        # ]
        # domain_country = [
        #     ("id", "!=", self.id),
        #     "&", ("location_field", "in", ["zip_id", "city_id", "state_id", "country_id"]), ("state_id", "=", self.state_id.id),
        # ]

        # if self.location_field == "zip_id":
        #     domain = domain_zip
        # elif self.location_field == "city_id":
        #     domain = domain_city
        # elif self.location_field == "state_id":
        #     domain = domain_state
        # else:
        #     domain = domain_country