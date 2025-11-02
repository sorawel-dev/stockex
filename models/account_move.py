# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    stockex_inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire Stockex',
        readonly=True,
        index=True,
        help='Inventaire Stockex qui a généré cette écriture comptable'
    )
