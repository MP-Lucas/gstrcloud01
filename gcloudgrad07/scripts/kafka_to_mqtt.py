import json
from confluent_kafka import Consumer, KafkaError
import paho.mqtt.client as mqtt

# Configurações do consumidor Kafka
consumer_conf = {
    'bootstrap.servers': 'broker:29092',
    'group.id': 'esp32_robots',  
    'auto.offset.reset': 'earliest'
}

# Tópico Kafka de interesse
kafka_topic = 'robot-control'

# Configurações do MQTT
mqtt_broker = 'mqtt-broker'
mqtt_port = 1883
mqtt_topic = 'esp32/control'



# Consumidor Kafka
kafka_consumer = Consumer(consumer_conf)
kafka_consumer.subscribe([kafka_topic])

# Cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# Consome mensagens do kafka e publica
# as mensagens no MQTT para o ESP32 consumir
def consume_kafka_and_publish_to_mqtt():
    while True:
        msg = kafka_consumer.poll(1.0)
        if msg is None:
            continue
        print("MOSQUITTO: ", msg.value())
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        else:
            # Publicar mensagem no MQTT
            mqtt_client.publish(mqtt_topic, msg.value().decode('utf-8'))

if __name__ == "__main__":
    try:
        consume_kafka_and_publish_to_mqtt()
    except KeyboardInterrupt:
        pass
    finally:
        kafka_consumer.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
