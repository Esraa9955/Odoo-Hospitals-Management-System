from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date
import re
class HospitalsSystem(models.Model):
  _name='hms.patient'
  _rec_name='first_name'

  first_name=fields.Char(required=True)
  last_name=fields.Char(required=True)
  address=fields.Text()
  age=fields.Integer(compute = 'calculate_age')
  graduate_age = fields.Integer(compute = 'calculate_age', store=True)
  birth_date=fields.Date()
  history=fields.Html()
  CR_ratio=fields.Float()
  blood_type=fields.Selection([('A', 'A'),('B', 'B'),('AB', 'AB'),('O', 'O')])
  pcr = fields.Boolean()
  image = fields.Binary()
  state = fields.Selection([('undetermined', 'Undetermined'), ('good', 'Good'), ('fair', 'Fair'), ('serious', 'Serious')], default='undetermined')
  email = fields.Char()
  department_id=fields.Many2one('hms.department')
  department_capacity=fields.Integer(related='department_id.capacity')
  doctors_ids = fields.Many2many(comodel_name='hms.doctors')
  log_history = fields.One2many('hms.patient.log', 'patient_id', string='Log History')
  _sql_constraints = [
    ('unique_patient_first_name', 'UNIQUE(first_name)', 'This patient is already existing'),
    ('unique_patient_email', 'UNIQUE(email)', 'This patient email is already existing'),
    ('age_check', 'CHECK(age >= 0)', 'Age cannot be less than zero'),
]

  def change_state(self):
    if self.state == 'undetermined':
      self.state='good'
    elif self.state == 'good':
      self.state='fair'
    elif self.state == 'fair':
      self.state='serious'
    else:
      self.state='undetermined'  
    self.set_history()

 


  @api.onchange('age')
  def check_pcr(self):
    for rec in self:
      if rec.age and rec.age < 30:
        rec.pcr=True
        Warning_msg={
          'title':'PCR Checked',
          'message':'PCR has been automatically checked as age is less than 30'
        }
        return {'warning':Warning_msg}
      


  



  @api.onchange('state')
  def log_state(self):
    for rec in self:
      rec.env['hms.patient.log'].create({
        'description':'State changed to %s'%rec.state,
        'patient_id':rec.id
      })
  


  @api.constrains('age')
  def check_age(self):
    for rec in self:
      if rec.age <= 0:
        raise ValidationError('age can ont be less than or equal zero')

  @api.depends('birth_date')
  def calculate_age(self):
    for rec in self:
      if rec.birth_date:
        today = date.today()
        rec.age = today.year - rec.birth_date.year -(
          (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
      else:
        rec.age=1
      rec.graduate_age =rec.age + 5


  def validate_email(self, email):
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError("Invalid email address: %s" % email)

  @api.onchange('email')
  def check_valid_email(self):
      for rec in self:
          rec.validate_email(rec.email)


  
class PatientLog(models.Model):
    _name = 'hms.patient.log'

    patient_id = fields.Many2one('hms.patient', string='Patient', ondelete='cascade')
    #created_by = fields.Many2one('res.users', string='Created By')
    #date = fields.Datetime(string='Date', default=fields.Datetime.now())
    description = fields.Text(string='Description')