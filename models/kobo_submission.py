# -*- coding: utf-8 -*-

from odoo import models, fields


class KoboSubmission(models.Model):
    _name = 'stockex.kobo.submission'
    _description = 'Soumission Kobo Collect'
    _order = 'submission_id desc, id desc'

    name = fields.Char(string='Nom', compute='_compute_name', store=False)

    config_id = fields.Many2one(
        comodel_name='stockex.kobo.config',
        string='Configuration',
        required=True,
        index=True,
        ondelete='cascade',
    )

    submission_id = fields.Integer(
        string='ID Soumission',
        index=True,
        help='Identifiant de la soumission retourné par Kobo'
    )

    submitted_at = fields.Datetime(
        string='Date de Soumission',
        index=True,
    )

    payload = fields.Text(
        string='Données (JSON)',
        help='Contenu JSON de la soumission'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('imported', 'Importé'),
            ('error', 'Erreur'),
        ],
        string='État',
        default='draft',
        index=True,
    )

    error_message = fields.Text(string='Erreur')

    def _compute_name(self):
        for rec in self:
            rec.name = f"Soumission #{rec.submission_id or rec.id}"
