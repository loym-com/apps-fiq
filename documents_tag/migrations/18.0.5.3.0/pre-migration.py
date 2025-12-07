from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    Copy old fields into new mixin fields:
    documents_tag_id  <- tag_id
    documents_tag_tooltip_translate  <- tag_tooltip_translate
    documents_tag_ids_filter  <- tag_ids_filter
    """

    cr.execute("""
        UPDATE documents_document
        SET
            documents_tag_id = tag_id,
            documents_tag_tooltip_translate = tag_tooltip_translate,
            documents_tag_color = tag_ids_color
        WHERE
            tag_id IS NOT NULL
            OR tag_tooltip_translate IS NOT NULL
            OR tag_color IS NOT NULL;
    """)
