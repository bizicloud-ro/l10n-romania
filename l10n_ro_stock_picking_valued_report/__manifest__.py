# Copyright (C) 2025 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Picking Valued Report",
    "version": "19.0.0.3.0",
    "category": "Localization",
    "summary": "Romania -  Stock Picking Valued Report",
    "author": "NextERP Romania,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "depends": [
        "base_comment_template",
        "purchase_stock",
        "sale_stock",
    ],
    "excludes": ["stock_picking_report_valued"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/l10n_ro_stock_picking_comment_template.xml",
        "views/stock_picking_view.xml",
        "views/report_delivery_document.xml",
        "views/report_picking.xml",
        "report/stock_picking_report_valued.xml",
    ],
    "installable": True,
    "sequence": 100,
    "development_status": "Mature",
    "maintainers": ["feketemihai"],
}
