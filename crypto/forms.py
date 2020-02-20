from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, HiddenField,IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired,  ValidationError
from wtforms.widgets import Select
from crypto import routes

def convert_float(sum):

    for num in sum:
        num = str(num).replace(',','')
        num = num.replace(')','')
        num = num.replace('(','')
        num = float(num)
    
    return num

def limit_money(form, field):

    print(form.come_from.data)
    if form.come_from.data != 'EUR':
        
        consulta_from_inicial = f"SELECT* FROM cripto WHERE from_currency = '{form.come_from.data}'"
        consulta_to_inicial = f"SELECT* FROM cripto WHERE to_currency = '{form.come_from.data}'"
        check_from = routes.query(consulta_from_inicial)
        check_to = routes.query(consulta_to_inicial)

        if check_from:
            
            consulta_from = f"SELECT SUM(from_quantity) FROM cripto WHERE from_currency = '{form.come_from.data}'"     
            quantity_from = routes.query(consulta_from)       
            quantity_from = convert_float(quantity_from)
    
        else:
            quantity_from = 0
        
        if check_to:

            consulta_to = f"SELECT SUM(to_quantity) FROM cripto WHERE to_currency = '{form.come_from.data}'"
            quantity_to = routes.query(consulta_to)
            quantity_to = convert_float(quantity_to)
        
        else:
            quantity_to = 0

        total_quantity = quantity_to - quantity_from

        result = total_quantity - float(form.Q_from.data)
    
        if total_quantity == 0:
            raise ValidationError(f'No tienes efectivo de {form.come_from.data}')
        
        if result < 0:
            raise ValidationError (f"'No tienes suficiente efectivo. Puedes invertir hasta {round(total_quantity-0.1,1)}  con {form.come_from.data}.")    
    

def validate_to_currency(form,field):

    select_coins = ['ETH','LTC','BCH','BNB','USDT','EOS','BSV','XLM','ADA','TXR']

    if form.come_from.data == form.go_to.data:
        raise ValidationError("No puedes tener la misma moneda en ambos huecos")

    if form.come_from.data == 'EUR' and form.go_to.data != 'BTC':
        raise ValidationError ("Con EUR solo puedes comprar BTC")

    if form.come_from.data in select_coins and form.go_to.data == 'EUR':
        raise ValidationError ("Solo puedes comprar EUR con BTC")

    
coins = [('EUR','EUR'),('BTC','BTC'),('ETH','ETH'),('LTC','LTC'),('BCH','BCH'),('BNB','BNB'),('USDT','USDT'),('EOS','EOS'),('BSV','BSV'),('XLM','XLM'),('ADA','ADA'),('TXR','TXR')]

def validate_Q(form,field):
    try:
        float(field.data)
    except:
        raise ValidationError(message ='Q must be a number')

class TaskForm(FlaskForm):
    
    
    come_from = SelectField('come_from', choices= coins,validators=[DataRequired()],widget=Select())
    go_to = SelectField('go_to', choices= coins,validators=[DataRequired(), validate_to_currency],widget=Select())
    Q_from = DecimalField('Q_from', validators=[DataRequired(),validate_Q,limit_money])
    
    submit = SubmitField('Calcular')
    accept = SubmitField('Aceptar')