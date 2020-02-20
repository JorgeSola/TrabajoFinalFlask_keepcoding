from crypto import app
from flask import render_template, request, redirect, url_for
from crypto.forms import TaskForm
import json
import requests
import sqlite3
from datetime import datetime
from datetime import date
import logging


logging.basicConfig(level=logging.INFO)

coins = ['BTC','ETH','LTC','BCH','BNB','USDT','EOS','BSV','XLM','ADA','TXR']

dt = datetime.now()
date = ("{}/{}/{}".format(str(dt.day).zfill(2),str(dt.month).zfill(2),dt.year))
time = ("{}:{}:{}".format(str(dt.hour).zfill(2),str(dt.minute).zfill(2),str(dt.second).zfill(2)))
apiKey = '7dfd8df7-76e7-4829-8fd7-b03aa6eedb03'

def puCalculate(start_Q,conversor):

    PU= float(start_Q)/conversor

    logging.debug(f'PU: {PU}') #logging

    return PU

def actualValueCalculate(actual_value_results):

    for individual_quantity in actual_value_results:

        individual_quantity = str(individual_quantity).replace(',)',"")
        individual_quantity = individual_quantity.replace('(', "")

        logging.debug(f'ITEM TO VALOR ACTUAL: {individual_quantity}') #logging

        return individual_quantity    

def inversionCalculate(inversion_results):

    overall_amount_inversion = 0

    for item in inversion_results:
        item = str(item).replace(',)',"")
        item = item.replace('(', "")

        logging.debug(f'ITEMS: {item}') #logging

        overall_amount_inversion += float(item)

    logging.debug(f'SUMA TOTAL: {overall_amount_inversion}') #logging

    return overall_amount_inversion

def conversorCalculate(url, final_coin):

    coin_info = requests.get(url)
    coin_info = coin_info.json()

    logging.debug(f'COIN INFO:{coin_info}') #logging

    conversor = coin_info['data']['quote'][final_coin]['price']

    logging.debug(f'conversor {conversor}') #logging

    return conversor

def query(consulta):
    
    d = []
    try:
        conn = sqlite3.connect('./data/base_date.db')
        c = conn.cursor()
        query = c.execute(consulta)
        for x in query:
            d.append(x)
        conn.close()
        return d

    except sqlite3.Error as e:
        logging.debug(f'Error type {e}')
        error = 'Error al conectarse a la base de datos'
        
        return render_template('index.html', error = error, information = None)
    

def insertTable(values):

    try:
        conn = sqlite3.connect('./data/base_date.db')
        c = conn.cursor()
        consulta = """INSERT INTO cripto VALUES (NULL,?,?,?,?,?,?,?)"""
        add = c.execute(consulta,values)
        conn.commit()
        conn.close()
        return add
    
    except sqlite3.Error as e:
        logging.debug(f'Error type {e}')
        error = 'Error al conectarse a la base de datos'
        
        return render_template('index.html', error = error, information = None)
 
@app.route('/')
def index():

    consulta = """SELECT * FROM cripto"""
    information = query(consulta)

    return render_template('index.html', info = information, error = None)
    

@app.route('/purchase',methods = ['GET','POST'])
def addForm():

    form = TaskForm(request.form)

    if request.method == 'GET':

        return  render_template('query.html', form = form)

    if request.method == 'POST':
        
        if form.validate():

            if form.data['submit']:

                start_coin = request.values.get('come_from')
                final_coin = request.values.get('go_to')
                start_Q = str(request.values.get('Q_from')).replace(",",'.')
                
                base_url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount='+start_Q+'&symbol='+start_coin+'&convert='+final_coin+'&CMC_PRO_API_KEY=7dfd8df7-76e7-4829-8fd7-b03aa6eedb03'

                conversor = conversorCalculate(base_url,final_coin)            
                PU = puCalculate(start_Q,conversor)

                return render_template('query.html', form = form, conversor = round(conversor,8), PU = round(PU,8)) 

            #HAY PARTES QUE SE REPITEN EN ACCEPT Y CALCULATE. DEBERÍA PODER UNIFICARLAS.

            if form.data['accept']:

                start_coin = str(request.values.get('come_from'))
                final_coin = str(request.values.get('go_to'))
                start_Q = str(request.values.get('Q_from'))

                base_url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount='+start_Q+'&symbol='+start_coin+'&convert='+final_coin+'&CMC_PRO_API_KEY=7dfd8df7-76e7-4829-8fd7-b03aa6eedb03'

                conversor = conversorCalculate(base_url, final_coin)
                PU = puCalculate(start_Q,conversor)

                valores = (date,time,start_coin,float(start_Q),final_coin,float(conversor),float(PU))
                insertTable(valores)

                return redirect(url_for('index'))
        else:
            return render_template('query.html', form = form)

@app.route('/status')
def investmentStatus():

    #CALCULO DE LA INVERSIÓN
    consulta_from_inversion = """ SELECT from_quantity FROM cripto WHERE from_currency = 'EUR' """
    inversion_from_results = query(consulta_from_inversion)

    consulta_to_inversion = """ SELECT to_quantity FROM cripto WHERE to_currency = 'EUR' """
    inversion_to_results = query(consulta_to_inversion)

    overall_amount_inversion = inversionCalculate(inversion_from_results) - inversionCalculate(inversion_to_results)

    logging.debug(f'RESULTS FOR EUROS: {overall_amount_inversion}') #logging     

    #CALCULO DEL VALOR ACTUAL
    from_quantity = 0
    to_quantity = 0 
    for crypto in coins:
        
        logging.debug(f'NAME CRYPTO: {crypto}') #logging

        individual_from_quantity = 0
        individual_to_quantity = 0

        consulta_from_valor_actual = """ SELECT from_quantity FROM cripto WHERE from_currency = '{}' """.format(crypto)
        consulta_to_valor_actual = """ SELECT to_quantity FROM cripto WHERE to_currency = '{}' """.format(crypto)

        actual_from_value_results = query(consulta_from_valor_actual)
        actual_to_value_results = query(consulta_to_valor_actual)

        logging.debug(f'RESULTS FOR CRYPTO FROM: {actual_from_value_results}') #logging
        logging.debug(f'RESULTS FOR CRYPTO TO: {actual_to_value_results}') #logging

        if actual_from_value_results:

            individual_from_quantity = actualValueCalculate(actual_from_value_results)

            base_url_from = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount='+str(individual_from_quantity)+'&symbol='+crypto+'&convert=EUR&CMC_PRO_API_KEY=7dfd8df7-76e7-4829-8fd7-b03aa6eedb03'
            
            conversor_from = conversorCalculate(base_url_from,'EUR')

            from_quantity += float(conversor_from)

        if actual_to_value_results:

            individual_to_quantity = actualValueCalculate(actual_to_value_results) 

            base_url_to = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount='+str(individual_to_quantity)+'&symbol='+crypto+'&convert=EUR&CMC_PRO_API_KEY=7dfd8df7-76e7-4829-8fd7-b03aa6eedb03'
        
            conversor_to = conversorCalculate(base_url_to,'EUR')  

            to_quantity += float(conversor_to)

    actual_value = to_quantity - from_quantity    

    return render_template('state.html', investments = overall_amount_inversion, actual_value = actual_value)
