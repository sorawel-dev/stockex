# -*- coding: utf-8 -*-
from odoo import models, fields

class EneoNetwork(models.Model):
    _name = 'stockex.eneo.network'
    _description = 'Réseau Interconnecté ENEO'
    _rec_name = 'name'

    name = fields.Char(string='Nom', required=True)
    code = fields.Selection(
        selection=[('RIS', 'RIS'), ('RIN', 'RIN')],
        string='Code',
        required=True,
    )
    active = fields.Boolean(string='Actif', default=True)
