from odoo import models, fields
from dateutil.relativedelta import relativedelta
from odoo import api
from odoo.exceptions import ValidationError

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "Test Model"

    name = fields.Char(string="Name",required=True)
    description = fields.Text(string="Descriptions")
    postcode = fields.Char()
    date_availability = fields.Date(string="Date",copy=False,
                                    default=lambda self:fields.Date.context_today(self)+relativedelta(months=3))
    expected_price = fields.Float(string="Expected Price", digits=(16,2),required=True)
    selling_price = fields.Float(string="Selling Price",digits=(16,2),copy=False,readonly=True)
    bedrooms = fields.Integer(string="QTY Bedrooms",default=2) #Vamos a probar que sea default 1
    living_area = fields.Integer(string="QTY Living Area")
    facades = fields.Integer(string="Facade")
    garage = fields.Boolean(string="Garage",default=True)
    garden = fields.Boolean(string="Garden",default=True)
    garden_area = fields.Integer(string="QTY Garden Area")
    garden_orientation = fields.Selection(string="Garden Orientation",
                                          selection=[("north","North"),
                                           ("south","South"),
                                           ("east","East"),
                                           ("west","West")])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            #Es importante que cada estado no debe llevar espacios
            #No puede ser offer received sino offer_received
            ('new', 'New'),
            ('offer_received','Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'),
            ('canceled','Canceled')
        ],
        string="State",
        required=True,
        copy=False,
        default='new'
    )

    property_type_id = fields.Many2one(
        #El campo many2one se usa para relacionar un campo con otro campo de otro modelo
        #El campo se ve como un dropdown
        "estate.property.type",
        string="Property Type"
    )

    tag_ids = fields.Many2many(
        #El campo se ve como una lista de etiquetas
    'estate.property.tag',
    string="Tags"
    )

    seller_id = fields.Many2one(
        'res.users',
        string="Seller", 
        default=lambda self:self.env.user #Esta es una forma de llamar al usuario actual loggeado.
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        copy=False
    )

    offer_ids = fields.One2many(
        #El campo se ve como una lista de ofertass
        'estate.property.offer',
        'property_id'
    )

    total_area = fields.Integer(string="Total Area",compute='_compute_total_area')

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        """
            Campo computado que calcula el area total de la propiedad.
        """
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.constrains('date_availability')
    def _check_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.context_today(self):
                raise ValidationError("La fecha no puede ser anterior a hoy.")