from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    Migrate existing parent_id/child_ids hierarchy to the new
    parent_ids/child_ids Many2many relation table.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    Tag = env['documents.tag']

    # Loop over all tags that have a parent
    for tag in Tag.search([('parent_id', '!=', False)]):
        parent = tag.parent_id
        if parent:
            # Insert into relation table if not already present
            cr.execute("""
                INSERT INTO documents_tag_hierarchy_rel (parent_id, child_id)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM documents_tag_hierarchy_rel
                    WHERE parent_id = %s AND child_id = %s
                )
            """, (parent.id, tag.id, parent.id, tag.id))
