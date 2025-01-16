# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Definimos modelo Liga Equipo, que almacenará información de cada equipo
class LigaEquipo(models.Model):
    _name = 'liga.equipo'
    _description = 'Equipo de la liga'
    _order = 'nombre'

    _rec_name = 'nombre'

    nombre = fields.Char('Nombre equipo', required=True, index=True)
    escudo = fields.Image('Escudo equipo', max_width=50, max_height=50)
    fecha_fundacion = fields.Date('Fecha fundación')
    descripcion = fields.Html('Descripción', sanitize=True, strip_style=False)

    victorias = fields.Integer(default=0)
    empates = fields.Integer(default=0)
    derrotas = fields.Integer(default=0)

    jugados = fields.Integer(compute="_compute_jugados", store=True)

    @api.depends('victorias', 'empates', 'derrotas')
    def _compute_jugados(self):
        for record in self:
            record.jugados = record.victorias + record.empates + record.derrotas

    puntos = fields.Integer(compute="_compute_puntos", default=0, store=True)

    @api.depends('victorias', 'empates')
    def _compute_puntos(self):
        for record in self:
            # Los puntos se calculan solo por victorias y empates
            record.puntos = record.victorias * 3 + record.empates

    goles_a_favor = fields.Integer()
    goles_en_contra = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (nombre)', 'El nombre del equipo ya existe.')
    ]

    @api.constrains('fecha_fundacion')
    def _check_release_date(self):
        for record in self:
            if record.fecha_fundacion and record.fecha_fundacion > fields.Date.today():
                raise ValidationError('La fecha de fundación debe ser anterior a la actual.')

    @api.model
    def actualizar_puntos_y_partidos(self):
        """
        Este método calcula los puntos de cada equipo en función de los partidos jugados.
        Los puntos se asignan de la siguiente manera:
        - Victoria: 3 puntos
        - Empate: 1 punto
        - Derrota: 0 puntos (no resta puntos)
        """
        for equipo in self.search([]):  # Recorremos todos los equipos
            victorias = 0
            empates = 0
            derrotas = 0
            goles_a_favor = 0
            goles_en_contra = 0
            partidos_jugados = 0

            # Buscamos los partidos en los que este equipo haya participado
            partidos_casa = self.env['liga.partido'].search([('equipo_casa', '=', equipo.id)])
            partidos_fuera = self.env['liga.partido'].search([('equipo_fuera', '=', equipo.id)])

            for partido in partidos_casa:
                partidos_jugados += 1
                goles_a_favor += partido.goles_casa
                goles_en_contra += partido.goles_fuera
                if partido.goles_casa > partido.goles_fuera:
                    victorias += 1
                elif partido.goles_casa < partido.goles_fuera:
                    derrotas += 1
                else:
                    empates += 1

            for partido in partidos_fuera:
                partidos_jugados += 1
                goles_a_favor += partido.goles_fuera
                goles_en_contra += partido.goles_casa
                if partido.goles_fuera > partido.goles_casa:
                    victorias += 1
                elif partido.goles_fuera < partido.goles_casa:
                    derrotas += 1
                else:
                    empates += 1

            # Actualizamos los valores del equipo
            equipo.write({
                'victorias': victorias,
                'empates': empates,
                'derrotas': derrotas,  # No se usan para calcular puntos
                'goles_a_favor': goles_a_favor,
                'goles_en_contra': goles_en_contra,
                'jugados': partidos_jugados,
                'puntos': victorias * 3 + empates  # Los puntos se calculan con base en victorias y empates
            })
