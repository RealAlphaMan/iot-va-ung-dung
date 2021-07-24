from flask import json, render_template, url_for, redirect, request, Flask, jsonify, send_file, send_from_directory, flash, Response
import pymysql
import textwrap
import datetime
import os
import shutil
import json
import time
import random
from datetime import datetime

app = Flask(__name__)

list_uname = []
checkLogin = False

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='iot')
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'iot'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def signIn():
    error = None
    global checkLogin
    checkLogin = False
    if request.method == 'POST':
        try:
            global _usr
            _usr = request.form['usr']
            _pwd = request.form['pwd']
            cursor = conn.cursor()
            query="SELECT password FROM user WHERE username = %s"
            cursor.execute(query, _usr)
            result = cursor.fetchone()
            if result[0] == _pwd:
                checkLogin = True
                list_uname.append(_usr)
                query = "SELECT userid FROM user WHERE username = %s"
                cursor.execute(query, _usr)
                result = cursor.fetchone()
                return redirect(url_for('show', userid = result[0]))
            else:
                error = "Invalid user or password"  
        except:
            error = "Invalid user or password"
    return render_template('LOGIN.html', error = error)

@app.route('/register', methods = ['GET', 'POST'])
def signUp():
    error = None
    global checkLogin
    checkLogin = False
    
    if request.method == 'POST':
        try:
            cursor = conn.cursor()
            _name = request.form['fullname']
            _usr = request.form['usr']
            _pwd = request.form['pwd']
            _con_pwd = request.form['con-pwd']
            if _name == '' or _usr == '' or _pwd == '' or _con_pwd == '':
                error = 'Please fill in all input'
            else:
                if _pwd != _con_pwd:
                    error = 'Password and Re-enter password are not equal'
                else: 
                    query = 'INSERT INTO user (name, username, password) VALUES (%s, %s, %s)'
                    cursor.execute(query, (_name, _usr, _pwd))
                    checkLogin = True
                    list_uname.append(_usr)
                    query = "SELECT userid FROM user WHERE username = %s"
                    cursor.execute(query, _usr)
                    result = cursor.fetchone()
                    return redirect(url_for('show', userid = result[0]))
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('REGISTER.html', error = error)

@app.route('/<userid>', methods = ['GET', 'POST'])
def show(userid):
    if checkLogin == True:
        cursor = conn.cursor()
        query = 'SELECT temp, humi, spo2, nhiptim, bodytemp, time FROM data WHERE userid = %s'
        cursor.execute(query, userid)
        result = cursor.fetchone()
        return render_template('homepage.html', temp = result[0 ], humi = result[1], spo2 = result[2], nhiptim = result[3], bodytemp = result[4], time = result[5])
    else:
        return redirect(url_for('signIn'))

@app.route('/temp-chart', methods = ['GET', 'POST'])
def tempChart():
    return render_template('temp.html')

@app.route('/temp-data/', methods = ['GET', 'POST'])
def tempData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set temp = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT temp FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/humi-chart', methods = ['GET', 'POST'])
def humiChart():
    return render_template('humi.html')

@app.route('/humi-data/', methods = ['GET', 'POST'])
def humiData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set humi = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT humi FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/spo2-chart', methods = ['GET', 'POST'])
def spo2Chart():
    return render_template('spo2.html')

@app.route('/spo2-data/', methods = ['GET', 'POST'])
def spo2Data(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set spo2 = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT spo2 FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/nhiptim-chart', methods = ['GET', 'POST'])
def nhiptimChart():
    return render_template('nhiptim.html')

@app.route('/nhiptim-data/', methods = ['GET', 'POST'])
def nhiptimData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set nhiptim = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT nhiptim FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/bodytemp-chart', methods = ['GET', 'POST'])
def bodytempChart():
    return render_template('bodytemp.html')

@app.route('/bodytemp-data/', methods = ['GET', 'POST'])
def bodytempData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set bodytemp = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT bodytemp FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/time-chart', methods = ['GET', 'POST'])
def timeChart():
    return render_template('time.html')

@app.route('/time-data/', methods = ['GET', 'POST'])
def timeData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            cursor.execute('update data set time = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT time FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5002)