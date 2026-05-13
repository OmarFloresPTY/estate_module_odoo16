from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Modulo Tipo de Propiedad"
    _order = 'sequence, name'

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'El nombre del tipo de propiedad debe ser único.'),
    ]

    name = fields.Char(string="Name",required=True)
    sequence = fields.Integer(string="Sequence", default=10)

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string="Properties"
    )
    