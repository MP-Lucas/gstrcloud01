#import de bibliotecas
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import psycopg
from datetime import datetime
from psycopg import Cursor
from psycopg.rows import dict_row


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

def subscriber(client):
    client.subscribe("esp32/dht/temperature")
    client.subscribe("esp32/dht/humidity")

def unsubscriber(client):
    client.unsubscribe("esp32/dht/temperature")
    client.unsubscribe("esp32/dht/humidity")

# Handler para quando o MQTT estiver conectado.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Os eventos de inscrição devem ser mantidos aqui a fim de que em
    # caso deconexão e reconecção as inscrições nos tópicos ocorram novamente.
    client.subscribe("esp32/dht/dbPopulate")
    subscriber(client)

#Handler de desconexão.
def on_disconnect(client, userdata, rc):
    unsubscriber(client)
    client.unsubscribe("esp32/dht/dbPopulate")
    print("disconnect succesful" + str(rc))

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")            

# Handler executado para cada vez que uma mensagem MQTT é recebida.
#Cada tópico tem tratamento próprio.
def on_message(client, userdata, message):
    if message.topic == "esp32/dht/dbPopulate":#envia as leituras para o banco
        dht_json = json.loads(message.payload)
        conn=psycopg.connect("postgresql://postgres:123@db:5432", row_factory=dict_row)
        c=conn.cursor()
        c.execute("INSERT INTO dhtreadings (temperature,humidity, currentdate, device) VALUES(%s, %s, %s, %s)", 
            (dht_json['temperature'],
                dht_json['humidity'], datetime.now(),'esp32') ) 
        conn.commit()   
        conn.close()

    #envia via socket as mensagens para as funções responsáveis no backend
    if message.topic == "esp32/dht/temperature":
        temp_json = json.loads(message.payload)
        socketio.emit('updateTempSensorData', {'value': temp_json, "date": get_current_datetime()})
        socketio.sleep(1)

    if message.topic == "esp32/dht/humidity":
        hum_json = json.loads(message.payload)
        socketio.emit('updateHumSensorData', {'value': hum_json, "date": get_current_datetime()})
        socketio.sleep(1)

#inicialização do cliente mqtt
mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect
mqttc.connect('gstrgrad01-mqtt-broker',1883,60)
mqttc.loop_start()

#Handler para o evento de filtro recebido do socket
@socketio.on('FilterDate')
def filteredGraph(data):
    #A função conecta no banco, executa e query e envia o retorno via socket para o JavaScript
    unsubscriber(mqttc)
    conn=psycopg.connect("postgresql://postgres:123@db:5432", row_factory=dict_row)
    c=conn.cursor()
    c.execute("SELECT AVG(temperature)::float as temperature, AVG(humidity)::float as humidity, DATE_TRUNC('hour', currentdate)::varchar as currentdate FROM dhtreadings WHERE DATE_TRUNC('day', currentdate) = (%s) group by DATE_TRUNC('hour', currentdate)::varchar", [data])
    r=c.fetchall()
    conn.close()
    if not r:  #Caso não haja retorno evento é disparado
        subscriber(mqttc)
        socketio.emit('No Data Returned', data)
    else: #Caso haja retorno, evento disparado
        socketio.emit('Filtered Data', r) 

#Handler para quando o botão Real Time é clicado
@socketio.on('RunItBack')
def rtUpdate():
    subscriber(mqttc)

#carrega o html da página
@app.route("/")
def index():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
