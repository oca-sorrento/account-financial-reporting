# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Tax Balance",
    "summary": "Compute tax balances based on date range",
    "version": "9.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.agilebg.com/",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "date_range",
    ],
    "data": [
        "wizard/open_tax_balances_view.xml",
        "views/account_tax_view.xml",
    ],
}
