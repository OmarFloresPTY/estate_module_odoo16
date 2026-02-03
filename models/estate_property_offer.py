from odoo import models, fields

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer Model'

    price = fields.Float(string="Price",digits=(16,2))
    state = fields.Selection(
        [
            ('accepted','Accepted'),
            ('refused','Refused')
        ],
        string="State"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partenr",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Estate Property",
        required=True
    )

