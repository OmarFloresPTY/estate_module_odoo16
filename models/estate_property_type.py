from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Modulo Tipo de Propiedad"

    name = fields.Char(string="Name",required=True)
    