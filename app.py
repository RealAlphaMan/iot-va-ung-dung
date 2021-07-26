from flask import json, render_template, url_for, redirect, request, Flask, jsonify, flash, Response
import pymysql
import datetime
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

app = Flask(__name__)

list_uname = []
checkLogin = False
userid = None

# MySQL config
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='iot')
 
# MQTT config
broker_address="broker.hivemq.com"
client = mqtt.Client("P1")

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def signIn():
    error = None
    global checkLogin
    global userid
    checkLogin = False
    if request.method == 'POST':
        try:
            global _usr
            # Get username and password from client
            _usr = request.form['usr']
            _pwd = request.form['pwd']
            cursor = conn.cursor()
            query="SELECT password FROM user WHERE username = %s"
            cursor.execute(query, _usr)
            result = cursor.fetchone()

            #Check if password is true
            if result[0] == _pwd:
                checkLogin = True
                list_uname.append(_usr)
                # Get userid
                query = "SELECT userid FROM user WHERE username = %s"
                cursor.execute(query, _usr)
                result = cursor.fetchone()
                userid = result[0] 
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
            
            #Get data from client
            _name = request.form['fullname']
            _usr = request.form['usr']
            _pwd = request.form['pwd']
            _con_pwd = request.form['con-pwd']
            if _name == '' or _usr == '' or _pwd == '' or _con_pwd == '':  #If not fill all input
                error = 'Please fill in all input'
            else:
                if _pwd != _con_pwd:
                    error = 'Password and Re-enter password are not equal'
                else: 
                    #Insert in to db
                    query = 'INSERT INTO user (userid, name, username, password) VALUES (3, %s, %s, %s)'
                    cursor.execute(query, (_name, _usr, _pwd))
                    #Create data for userid
                    query = 'INSERT INTO data (id, userid, temp, humi, spo2, nhiptim, bodytemp, time) VALUES (4, 3, 0, 0, 0, 0, 0, 0)'
                    cursor.execute(query)
                    checkLogin = True
                    list_uname.append(_usr)
                    # Get userid
                    query = "SELECT userid FROM user WHERE username = %s"
                    cursor.execute(query, _usr)
                    result = cursor.fetchone()
                    userid = result[0]
                    return redirect(url_for('show', userid = userid))
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('REGISTER.html', error = error)

@app.route('/<userid>', methods = ['GET', 'POST'])
def show(userid):
    if checkLogin == True:
        return render_template('homepage.html')
    else:
        return redirect(url_for('signIn'))

@app.route('/realtime-data', methods = ['GET', 'POST'])
def realtimeData():
    def generate_data():
        while True:
            #Get realtime data for temperature from broker HiveMQ
            def on_connect(client, userdata, flags, rc):
                if rc==0:
                    pass
                else:
                    print("Client is not connnected")

            def on_message(client, userdata, message):
                global temp_subcribe
                temp_subcribe = str(message.payload.decode("utf-8"))

            broker_addr = "broker.hivemq.com"
            client = mqtt.Client("a")
            client.on_message = on_message
            client.connect(broker_addr, 1883)
            client.on_connect = on_connect
            client.subscribe("/iot/user1/data/temp")
            client.loop_start()
            time.sleep(10)

            client.loop_stop()
            time.sleep(1)
            # Send data realtime
            json_data = json.dumps({'temp': temp_subcribe, 'humi': random.uniform(64, 67), 'spo2': random.uniform(19, 21), 'nhiptim': random.uniform(57, 65),'bodytemp': random.uniform(36, 38)})
            yield f"data:{json_data}\n\n"
        
    return Response(generate_data(), mimetype='text/event-stream')

@app.route('/temp-chart', methods = ['GET', 'POST'])
def tempChart():
    return render_template('temp.html')

@app.route('/temp-data/', methods = ['GET', 'POST'])
def tempData(userid = 1):
    cursor = conn.cursor()
    # Get real time data for temperature
    def get_data():
        while True:
            def on_connect(client, userdata, flags, rc):
                if rc==0:
                    pass
                else:
                    print("Client is not connnected")

            def on_message(client, userdata, message):
                global temp_subcribe
                temp_subcribe = str(message.payload.decode("utf-8"))

            broker_addr = "broker.hivemq.com"
            client = mqtt.Client("a")
            client.on_message = on_message
            client.connect(broker_addr, 1883)
            client.on_connect = on_connect
            client.subscribe("/iot/user1/data/temp")
            client.loop_start()
            time.sleep(10)
            client.loop_stop()

            cursor.execute('update data set temp = %s where userid = %s',(temp_subcribe, userid))
            query = 'SELECT temp FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(get_data(), mimetype='text/event-stream')

@app.route('/humi-chart', methods = ['GET', 'POST'])
def humiChart():
    return render_template('humi.html')

@app.route('/humi-data/', methods = ['GET', 'POST'])
def humiData(userid = 1):
    cursor = conn.cursor()
    def generate_random_data():
        while True:
            # Get random data for humidity
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
            # Get random data for Spo2
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
            # Get random data for Heart beat
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
            # Get random data for Body temperature
            cursor.execute('update data set bodytemp = %s where userid = %s',(random.random()*100, userid))

            query = 'SELECT bodytemp FROM data WHERE userid = %s'
            cursor.execute(query, userid)
            result = cursor.fetchone()
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': result[0]})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5000)