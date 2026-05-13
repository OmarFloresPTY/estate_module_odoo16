from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "Test Model"
    _order = 'id desc'

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

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'El precio esperado debe ser estrictamente positivo.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'El precio de venta debe ser positivo.'),
    ]

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
    best_price = fields.Float(string="Best Price",compute='_compute_best_price') 

    @api.onchange('garden') #Los onchange son campos que se actualizan cuando se cambia el valor de otro campo unicamente en la vista form
    def _onchange_garden(self):
        """
            Cambia el valor de garden_area y garden_orientation si garden es True.
        """
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        """
            Campo computado que calcula el mejor precio de la propiedad.
        """
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price')) #El metodo mapped se usa para obtener los valores de un campo de un modelo relacionado. En este caso, se obtiene el valor los valores del campo 'price' de todos los registros relacionados con el campo 'offer_ids' en una lista.
            else:
                record.best_price = 0

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        """
            Campo computado que calcula el area total de la propiedad.
        """
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                # comparar el precio de venta con el 90% del precio esperado.Si es menor, lanza un error.
                # -1 si value1 < value2
                #  0 si value1 == value2
                #  1 si value1 > value2
                raise ValidationError("El precio de venta no puede ser inferior al 90% del precio esperado.")

    @api.constrains('date_availability')
    def _check_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.context_today(self):
                raise ValidationError("La fecha no puede ser anterior a hoy.")
    
    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Una propiedad cancelada no puede ser marcada como vendida.")
            record.state = 'sold'

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Una propiedad vendida no puede ser cancelada.")
            record.state = 'canceled'