# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPickingValued(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.account_fiscal_country_id = cls.env.ref("base.ro")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        tax_group = cls.env["account.tax.group"].create(
            {"name": "Test VAT", "country_id": cls.env.ref("base.ro").id}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Test VAT 19%",
                "amount": 19,
                "type_tax_use": "sale",
                "tax_group_id": tax_group.id,
            }
        )
        cls.purchase_tax = cls.env["account.tax"].create(
            {
                "name": "Test VAT 19% (purchase)",
                "amount": 19,
                "type_tax_use": "purchase",
                "tax_group_id": tax_group.id,
            }
        )
        # Deductible VAT: without an account, the tax would be added to the stock value
        vat_account = cls.env["account.account"].create(
            {
                "name": "Test Deductible VAT",
                "code": "442600",
                "account_type": "asset_current",
            }
        )
        cls.purchase_tax.invoice_repartition_line_ids.filtered(
            lambda line: line.repartition_type == "tax"
        ).account_id = vat_account
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "standard_price": 5.0,
                "list_price": 10.0,
                "taxes_id": [Command.set(cls.tax.ids)],
                "supplier_taxes_id": [Command.set(cls.purchase_tax.ids)],
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )

    def test_delivery_valued_from_sale_line(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, 10
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 3,
                            "price_unit": 10.0,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        picking = sale.picking_ids

        self.assertEqual(picking.move_line_ids.l10n_ro_price_unit, 10.0)
        self.assertAlmostEqual(picking.l10n_ro_amount_untaxed, 30.0)
        self.assertAlmostEqual(picking.l10n_ro_amount_tax, 5.7)
        self.assertAlmostEqual(picking.l10n_ro_amount_total, 35.7)
        self.assertIn(
            self.env.ref(
                "l10n_ro_stock_picking_valued_report.l10n_ro_picking_delivery_internTransfer"
            ),
            picking.comment_template_ids,
        )

    def test_receipt_valued_from_stock_move(self):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 2,
                            "price_unit": 5.0,
                        }
                    )
                ],
            }
        )
        purchase.button_confirm()
        picking = purchase.picking_ids
        picking.move_ids.quantity = 2
        picking.move_ids.picked = True
        picking.button_validate()

        self.assertEqual(picking.move_line_ids.l10n_ro_price_unit, 5.0)
        self.assertAlmostEqual(picking.l10n_ro_amount_untaxed, 10.0)
        self.assertAlmostEqual(picking.l10n_ro_amount_tax, 1.9)
        self.assertAlmostEqual(picking.l10n_ro_amount_total, 11.9)
