from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name ="estate.property.tag"
    _description = "Proterty Tag"
    _order = 'name'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'El nombre de la etiqueta debe ser único.'),
    ]

    name = fields.Char(string="Tag",required=True)