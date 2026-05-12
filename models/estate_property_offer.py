from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

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

    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(string="Date Deadline", compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            # Si el registro es nuevo, create_date es None. Usamos la fecha de hoy.
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = start_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            # Aseguramos que tratamos con objetos de fecha (Date)
            create_date = fields.Date.to_date(record.create_date) if record.create_date else fields.Date.today()
            if record.date_deadline and create_date:
                # La resta de dos objetos Date devuelve un timedelta de Python
                delta = record.date_deadline - create_date
                record.validity = delta.days


    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Estate Property",
        required=True
    )
    
    def action_accept(self):
        for record in self:
            if record.property_id.offer_ids.filtered(lambda o: o.state == 'accepted' and o.id != record.id):
                raise UserError("Ya existe una oferta aceptada para esta propiedad.")
            record.state = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'

    def action_refuse(self):
        for record in self:
            record.state = 'refused'