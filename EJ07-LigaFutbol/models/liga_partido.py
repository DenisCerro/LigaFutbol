from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LigaPartido(models.Model):
    _name = 'liga.partido'
    _description = 'Un partido de la liga'

    equipo_casa = fields.Many2one(
        'liga.equipo',
        string='Equipo local',
    )
    goles_casa = fields.Integer()

    equipo_fuera = fields.Many2one(
        'liga.equipo',
        string='Equipo visitante',
    )
    goles_fuera = fields.Integer()
    
    def print_report(self):
        # Definir aquí la lógica para generar el informe en PDF
        return self.env.ref('EJ07-LigaFutbol.report_partido').report_action(self)
        
    @api.constrains('equipo_casa', 'equipo_fuera')
    def _check_equipos_diferentes(self):
        for record in self:
            if not record.equipo_casa or not record.equipo_fuera:
                raise ValidationError('Ambos equipos deben estar seleccionados.')
            if record.equipo_casa == record.equipo_fuera:
                raise ValidationError('Los equipos deben ser diferentes en un partido.')

    def actualizoRegistrosEquipo(self):
        for recordEquipo in self.env['liga.equipo'].search([]):
            recordEquipo.victorias = 0
            recordEquipo.empates = 0
            recordEquipo.derrotas = 0
            recordEquipo.goles_a_favor = 0
            recordEquipo.goles_en_contra = 0
            recordEquipo.jugados = 0  # Inicializamos el contador de partidos jugados

            for recordPartido in self.env['liga.partido'].search([]):
                if recordPartido.equipo_casa.nombre == recordEquipo.nombre:
                    if recordPartido.goles_casa > recordPartido.goles_fuera:
                        if recordPartido.goles_casa - recordPartido.goles_fuera >= 4:
                            recordEquipo.victorias += 4
                        else:
                            recordEquipo.victorias += 1
                    elif recordPartido.goles_casa < recordPartido.goles_fuera:
                        if recordPartido.goles_fuera - recordPartido.goles_casa >= 4:
                            recordEquipo.derrotas -= 1  # Penalizamos con -1 partido jugado en lugar de -1 puntos
                        else:
                            recordEquipo.derrotas += 1
                    else:
                        recordEquipo.empates += 1

                    # Sumamos goles a favor y en contra
                    recordEquipo.goles_a_favor += recordPartido.goles_casa
                    recordEquipo.goles_en_contra += recordPartido.goles_fuera
                    recordEquipo.jugados += 1  # Incrementamos partidos jugados

                if recordPartido.equipo_fuera.nombre == recordEquipo.nombre:
                    if recordPartido.goles_fuera > recordPartido.goles_casa:
                        if recordPartido.goles_fuera - recordPartido.goles_casa >= 4:
                            recordEquipo.victorias += 4
                        else:
                            recordEquipo.victorias += 1
                    elif recordPartido.goles_fuera < recordPartido.goles_casa:
                        if recordPartido.goles_casa - recordPartido.goles_fuera >= 4:
                            recordEquipo.derrotas -= 1  # Penalizamos con -1 partido jugado en lugar de -1 puntos
                        else:
                            recordEquipo.derrotas += 1
                    else:
                        recordEquipo.empates += 1

                    # Sumamos goles a favor y en contra
                    recordEquipo.goles_a_favor += recordPartido.goles_fuera
                    recordEquipo.goles_en_contra += recordPartido.goles_casa
                    recordEquipo.jugados += 1  # Incrementamos partidos jugados

    def sumar_goles_local(self):
        for partido in self:
            partido.goles_casa += 2
        self.actualizoRegistrosEquipo()

    def sumar_goles_visitante(self):
        for partido in self:
            partido.goles_fuera += 2
        self.actualizoRegistrosEquipo()
