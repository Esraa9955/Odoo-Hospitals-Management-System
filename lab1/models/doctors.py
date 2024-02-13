from odoo import models,fields
class Doctors(models.Model):
  _name='hms.doctors'
  _rec_name='first_name'

  first_name=fields.Char()
  last_name=fields.Char()
  image = fields.Binary()
  patients_ids=fields.Many2many('hms.patient')