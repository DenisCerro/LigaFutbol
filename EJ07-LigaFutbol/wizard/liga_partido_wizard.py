from odoo import models, fields, api

class LigaPartidoWizard(models.TransientModel):
    _name = 'liga.partido.wizard'
    _description = 'Wizard para crear un nuevo partido'

    equipo_casa = fields.Many2one('liga.equipo', string='Equipo Local', required=True)
    equipo_fuera = fields.Many2one('liga.equipo', string='Equipo Visitante', required=True)
    goles_casa = fields.Integer(string='Goles Locales', default=0)
    goles_fuera = fields.Integer(string='Goles Visitantes', default=0)

    @api.constrains('equipo_casa', 'equipo_fuera')
    def _check_equipos_diferentes(self):
        if self.equipo_casa == self.equipo_fuera:
            raise ValidationError("Los equipos deben ser diferentes.")

    def crear_partido(self):
        partido = self.env['liga.partido'].create({
            'equipo_casa': self.equipo_casa.id,
            'equipo_fuera': self.equipo_fuera.id,
            'goles_casa': self.goles_casa,
            'goles_fuera': self.goles_fuera,
        })
        return partido

