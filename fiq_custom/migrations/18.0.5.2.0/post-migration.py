import logging
from openupgrade import openupgrade_logging, logged_query
from openupgradelib import openupgrade_rename_fields

_logger = logging.getLogger(__name__)
openupgrade_logging()


def migrate(cr, version):
    """Remove res.users field 'source_id' from the database."""
    
    # Delete the field from ir.model.fields
    cr.execute(
        "DELETE FROM ir_model_fields WHERE model = %s AND name = %s",
        ("res.users", "source_id")
    )
    _logger.info("Deleted 'source_id' from ir.model.fields")
    
    # Drop the column from res_users table
    cr.execute("ALTER TABLE res_users DROP COLUMN IF EXISTS source_id")
    _logger.info("Dropped 'source_id' column from res_users table")
