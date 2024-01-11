from odoo import tools, models, fields, api, _
from datetime import datetime,date
import requests
from py_bcu.bcu_cotizacion import get_cotizacion

from odoo.exceptions import ValidationError

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def get_bcu_exchange_rate(self):
        mail_param = self.env['ir.config_parameter'].get_param('mail_administrador', False)
        if not mail_param:
            raise ValidationError('Falta el parametro mail_administrador')
        currency_id = self.env.ref('base.USD')
        try:
            cot = get_cotizacion()
            exchange_rate = cot[1]
            vals = {
                   'name': str(date.today()),
                   'rate': 1 / (exchange_rate or 1),
                   'currency_id': currency_id.id,
                   }
            new_rate = self.env['res.currency.rate'].search([
                ('name','=',str(date.today())),
                ('currency_id','=',currency_id.id)])
            if not new_rate:
                res = self.env['res.currency.rate'].create(vals)
            else:
                new_rate.write(vals)
        except:
            vals_mail = {
                    'body': 'Problemas actualizando el USD desde el BCU',
                    'body_html': '<p>Problemas actualizando el USD desde el BCU</p>',
                    'subject': 'Problemas actualizando el USD desde el BCU>',
                    'email_to': mail_param,
                    'res_id': currency_id.id,
                    'model': self.env.ref('base.model_res_currency').id,
                    }
            mail_id = self.env['mail.mail'].create(vals_mail)
            mail_id.send()
